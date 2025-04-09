import sqlite3
import pandas as pd
import torch
from flask import jsonify
from models.lstm_model import LSTMModel
import os

# Đường dẫn tuyệt đối tới cơ sở dữ liệu
db_path = os.path.join(os.getcwd(), 'backend', 'database', 'm5_forecasting.db')

# Load mô hình LSTM
model_path = "lstm_model.pth"
input_size = 1
hidden_size = 512
output_size = 1
model = LSTMModel(input_size, hidden_size, output_size)
model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
model.eval()

# Kết nối đến cơ sở dữ liệu SQLite và lấy dữ liệu lịch sử
def get_historical_data():
    try:
        print("Đang kết nối tới cơ sở dữ liệu:", db_path)
        conn = sqlite3.connect(db_path)
        query = "SELECT name FROM sqlite_master WHERE type='table';"
        
        # Kiểm tra danh sách bảng có trong cơ sở dữ liệu
        tables = pd.read_sql(query, conn)
        print("Danh sách bảng trong cơ sở dữ liệu:", tables)

        # Truy vấn bảng normalized_train_data
        query = "SELECT * FROM normalized_train_data"
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        print("Lỗi khi kết nối cơ sở dữ liệu:", e)
        return pd.DataFrame()  # Trả về DataFrame rỗng nếu có lỗi

# Hàm dự báo
def predict():
    try:
        # Lấy dữ liệu lịch sử
        historical_data = get_historical_data()
        
        if historical_data.empty:
            return jsonify({"error": "Không có dữ liệu lịch sử đủ để dự báo"}), 400
        
        # In ra dữ liệu lịch sử để kiểm tra
        print(historical_data.head())

        # Chuyển dữ liệu thành tensor cho mô hình
        input_data = torch.tensor(historical_data['normalized_value'].values).unsqueeze(0).float()

        # Dự báo
        with torch.no_grad():  # Không cần tính toán gradient khi dự báo
            predictions = model(input_data).tolist()

        return jsonify({'predictions': predictions})

    except Exception as e:
        print("Lỗi khi dự báo:", e)
        return jsonify({"error": str(e)}), 500
