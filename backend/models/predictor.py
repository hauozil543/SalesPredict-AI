import torch
from torch.amp import autocast
import pickle
import numpy as np
from models.lstm_model import LSTMEmbForecast

class Predictor:
    def __init__(self, model_path='best_model.pth', params_path='model_params.txt'):
        # Đọc tham số mô hình
        with open(params_path, 'r') as f:
            lines = f.readlines()
            self.num_items = int(lines[0].split(': ')[1])
            self.num_stores = int(lines[1].split(': ')[1])
            self.feature_cols = eval(lines[2].split(': ')[1])

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
            hidden_size=128
        ).to(self.device)
        self.model.load_state_dict(torch.load(model_path))
        self.model.eval()

    def predict(self, X_num, X_item, X_store):
        X_num = torch.tensor(X_num, dtype=torch.float32).to(self.device)
        X_item = torch.tensor(X_item, dtype=torch.int64).to(self.device)
        X_store = torch.tensor(X_store, dtype=torch.int64).to(self.device)

        with torch.no_grad(), autocast(device_type='cuda' if torch.cuda.is_available() else 'cpu'):
            pred = self.model(X_num, X_item, X_store)
        pred = pred.cpu().numpy()

        # Tạo mảng giả với tất cả các cột mà scaler đã fit
        # scaler fit trên ['sell_price', 'sales', 'sales_lag_7', 'sales_lag_14', 'sales_lag_28', 'rolling_mean_7']
        # Chỉ cần giá trị 'sales', các cột khác để là 0
        dummy_array = np.zeros((1, 6))  # 6 cột trong numeric_cols
        dummy_array[0, 1] = pred  # Cột thứ 1 là 'sales'

        # Khôi phục giá trị gốc
        pred_orig = self.scaler.inverse_transform(dummy_array)
        return float(pred_orig[0, 1])  # Lấy giá trị gốc của cột 'sales'