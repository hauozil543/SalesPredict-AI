import torch
import torch.nn as nn
from torch.amp import autocast  # Sửa import: từ torch.cuda.amp thành torch.amp
import numpy as np
import pickle

class LSTMEmbForecast(nn.Module):
    def __init__(self, n_items, n_stores, embed_dim, num_feats, hidden_size, num_layers=2):
        super().__init__()
        self.item_emb = nn.Embedding(n_items, embed_dim)
        self.store_emb = nn.Embedding(n_stores, embed_dim)
        input_size = embed_dim * 2 + num_feats
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers=num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, 1)

    def forward(self, X_num, X_item, X_store):
        item_emb = self.item_emb(X_item)
        store_emb = self.store_emb(X_store)
        X = torch.cat((X_num, item_emb, store_emb), dim=-1)
        lstm_out, _ = self.lstm(X)
        out = self.fc(lstm_out[:, -1, :])
        return out.squeeze()

class Predictor:
    def __init__(self, model_path='best_model.pth', params_path='model_params.txt'):
        try:
            # Đọc tham số mô hình
            with open(params_path, 'r') as f:
                lines = f.readlines()
                if len(lines) < 3:
                    raise ValueError(f"model_params.txt must have at least 3 lines, got {len(lines)}")

                # Đọc num_items
                num_items_line = lines[0].strip()
                if not num_items_line.startswith('num_items: '):
                    raise ValueError("First line must start with 'num_items: '")
                self.num_items = int(num_items_line.split(': ')[1])

                # Đọc num_stores
                num_stores_line = lines[1].strip()
                if not num_stores_line.startswith('num_stores: '):
                    raise ValueError("Second line must start with 'num_stores: '")
                self.num_stores = int(num_stores_line.split(': ')[1])

                # Đọc feature_cols
                feature_cols_line = lines[2].strip()
                if not feature_cols_line.startswith('feature_cols: '):
                    raise ValueError("Third line must start with 'feature_cols: '")
                self.feature_cols = eval(feature_cols_line.split(': ')[1])

            # Tải scaler
            with open('utils/scaler.pkl', 'rb') as f:
                self.scaler = pickle.load(f)

            # Tải mô hình
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
            self.model = LSTMEmbForecast(
                n_items=self.num_items,
                n_stores=self.num_stores,
                embed_dim=16,
                num_feats=len(self.feature_cols),
                hidden_size=128,
                num_layers=2
            ).to(self.device)
            self.model.load_state_dict(torch.load(model_path, map_location=self.device))
            self.model.eval()
        except Exception as e:
            raise ValueError(f"Failed to initialize Predictor: {str(e)}")

    def predict(self, X_num, X_item, X_store):
        # Chuyển đổi dữ liệu thành tensor
        X_num = torch.tensor(X_num, dtype=torch.float32).to(self.device)
        X_item = torch.tensor(X_item, dtype=torch.int64).to(self.device)
        X_store = torch.tensor(X_store, dtype=torch.int64).to(self.device)

        # Dự báo với autocast sửa đổi
        with torch.no_grad():
            # Sử dụng torch.amp.autocast với cú pháp mới
            device_type = 'cuda' if torch.cuda.is_available() else 'cpu'
            with autocast(device_type=device_type, enabled=True):
                pred = self.model(X_num, X_item, X_store)
        pred = pred.cpu().numpy()

        # Tạo mảng giả để khôi phục giá trị gốc
        dummy_array = np.zeros((1, 6))  # 6 cột trong numeric_cols: ['sell_price', 'sales', 'sales_lag_7', 'sales_lag_14', 'sales_lag_28', 'rolling_mean_7']
        dummy_array[0, 1] = pred  # Cột thứ 1 là 'sales'

        # Khôi phục giá trị gốc
        pred_orig = self.scaler.inverse_transform(dummy_array)
        return float(pred_orig[0, 1])  # Lấy giá trị gốc của cột 'sales'