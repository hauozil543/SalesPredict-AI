import pandas as pd
import numpy as np
import torch
from models.lstm_model import LSTMEmbForecast
from datetime import datetime, timedelta

class Predictor:
    def __init__(self, model_path, item_enc, store_enc, scaler):
        self.item_enc = item_enc
        self.store_enc = store_enc
        self.scaler = scaler

        # Tải thông số mô hình
        self.device = torch.device('cpu')
        self.window_size = 28
        self.feature_cols = ['day', 'weekday_sin', 'weekday_cos', 'month_sin', 'month_cos', 'week',
                            'sales_lag_7', 'sales_lag_14', 'sales_lag_28', 'rolling_mean_7', 'rolling_mean_14',
                            'sell_price', 'event', 'snap']
        
        # Tải mô hình
        self.model = LSTMEmbForecast(
            n_items=len(item_enc),
            n_stores=len(store_enc),
            embed_dim=16,
            num_feats=len(self.feature_cols),
            hidden_size=64,
            num_layers=2,
            dropout=0.25
        ).to(self.device)
        self.model.load_state_dict(torch.load(model_path, map_location=self.device))
        self.model.eval()

    def create_future_features(self, historical_data, forecast_days):
        """
        Tạo dữ liệu cho các ngày tương lai dựa trên dữ liệu lịch sử.
        """
        last_date = pd.to_datetime(historical_data['date'].iloc[-1])
        future_dates = [last_date + timedelta(days=i) for i in range(1, forecast_days + 1)]
        future_df = pd.DataFrame({
            'date': future_dates,
            'item_idx': historical_data['item_idx'].iloc[-1],
            'store_idx': historical_data['store_idx'].iloc[-1],
            'sell_price': historical_data['sell_price'].iloc[-1],
            'event': 0,
            'snap': 0
        })

        # Tính các đặc trưng thời gian
        future_df['day'] = future_df['date'].dt.day
        future_df['month'] = future_df['date'].dt.month
        future_df['weekday'] = future_df['date'].dt.weekday
        future_df['week'] = future_df['date'].dt.isocalendar().week.astype('int64')
        future_df['weekday_sin'] = np.sin(2 * np.pi * future_df['weekday'] / 7)
        future_df['weekday_cos'] = np.cos(2 * np.pi * future_df['weekday'] / 7)
        future_df['month_sin'] = np.sin(2 * np.pi * future_df['month'] / 12)
        future_df['month_cos'] = np.cos(2 * np.pi * future_df['month'] / 12)

        # Ban đầu, để các cột sales và lag là 0
        future_df['sales'] = 0
        for lag in [7, 14, 28]:
            future_df[f'sales_lag_{lag}'] = 0
        future_df['rolling_mean_7'] = 0
        future_df['rolling_mean_14'] = 0

        return future_df

    def predict(self, historical_data, forecast_days):
        """
        Dự báo doanh số cho forecast_days ngày tiếp theo.
        """
        predictions = []
        data = historical_data.copy()

        # Tạo dữ liệu cho các ngày tương lai
        future_df = self.create_future_features(data, forecast_days)
        full_data = pd.concat([data, future_df], ignore_index=True)

        # Chuyển đổi kiểu dữ liệu cho các cột
        for col in self.feature_cols:
            full_data[col] = pd.to_numeric(full_data[col], errors='coerce').fillna(0)
        full_data['item_idx'] = pd.to_numeric(full_data['item_idx'], errors='coerce').fillna(0).astype(int)
        full_data['store_idx'] = pd.to_numeric(full_data['store_idx'], errors='coerce').fillna(0).astype(int)

        for i in range(forecast_days):
            # Lấy window dữ liệu để dự báo
            start_idx = len(full_data) - self.window_size - forecast_days + i
            window_data = full_data.iloc[start_idx:start_idx + self.window_size]

            # Chuẩn bị dữ liệu đầu vào cho mô hình
            X_num = torch.FloatTensor(window_data[self.feature_cols].values).unsqueeze(0).to(self.device)
            X_item = torch.LongTensor(window_data['item_idx'].values).unsqueeze(0).to(self.device)
            X_store = torch.LongTensor(window_data['store_idx'].values).unsqueeze(0).to(self.device)

            # Dự báo
            with torch.no_grad():
                pred = self.model(X_num, X_item, X_store).item()

            # Giải chuẩn hóa kết quả (chỉ áp dụng cho cột sales)
            dummy_input = np.zeros((1, 7))  # Scaler kỳ vọng 7 cột
            dummy_input[0, 0] = pred  # Cột đầu tiên là sales
            pred_unscaled = self.scaler.inverse_transform(dummy_input)[0][0]  # Lấy giá trị sales đã giải chuẩn hóa
            print("pred:", pred)
            print("pred_unscaled:", pred_unscaled)
            predictions.append(float(pred_unscaled))  # Lưu giá trị đã giải chuẩn hóa

            # Cập nhật sales với giá trị chuẩn hóa cho lần dự báo tiếp theo
            pred_scaled = pred  # Giá trị đã chuẩn hóa
            full_data.loc[len(data) + i, 'sales'] = pred_scaled

            # Cập nhật lag features
            for lag in [7, 14, 28]:
                if len(data) + i - lag >= 0:
                    full_data.loc[len(data) + i, f'sales_lag_{lag}'] = full_data.loc[len(data) + i - lag, 'sales']

            # Cập nhật rolling mean
            if len(data) + i >= 7:
                rolling_data_7 = full_data.loc[len(data) + i - 7:len(data) + i - 1, 'sales']
                full_data.loc[len(data) + i, 'rolling_mean_7'] = rolling_data_7.mean()
            if len(data) + i >= 14:
                rolling_data_14 = full_data.loc[len(data) + i - 14:len(data) + i - 1, 'sales']
                full_data.loc[len(data) + i, 'rolling_mean_14'] = rolling_data_14.mean()

        return predictions