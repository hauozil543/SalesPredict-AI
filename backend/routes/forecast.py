from flask import Blueprint, request, jsonify
import torch
import pandas as pd
import sqlite3
import os
from models.lstm_model import LSTMModel

# Tạo Blueprint mà không đặt url_prefix ở đây!
forecast_bp = Blueprint('forecast', __name__)

# Đường dẫn model và database
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, '..', 'lstm_model.pth')
DB_PATH = os.path.join(BASE_DIR, '..', 'database', 'm5_forecasting.db')

# Load mô hình LSTM
input_size = 1
hidden_size = 512
output_size = 1

model = LSTMModel(input_size, hidden_size, output_size)
model.load_state_dict(torch.load(MODEL_PATH, map_location=torch.device('cpu')))
model.eval()

# API dự báo
@forecast_bp.route('/predict', methods=['POST'])  # ✅ Không có /api ở đây
def predict():
    try:
        item_id = request.json.get('item_id')
        if not item_id:
            return jsonify({'error': 'Missing item_id'}), 400

        # Truy vấn dữ liệu từ SQLite
        conn = sqlite3.connect(DB_PATH)
        query = """
            SELECT normalized_value 
            FROM normalized_train_data 
            WHERE item_id = ? 
            ORDER BY day DESC 
            LIMIT 28
        """
        df = pd.read_sql(query, conn, params=(item_id,))
        conn.close()

        if df.empty or len(df) < 28:
            return jsonify({'error': 'Không đủ dữ liệu cho item này'}), 400

        # Đảo ngược dữ liệu vì ORDER BY DESC
        df = df.iloc[::-1]

        # Chuẩn bị dữ liệu đầu vào: [1, 28, 1]
        input_tensor = torch.tensor(df['normalized_value'].values).unsqueeze(0).unsqueeze(2).float()

        with torch.no_grad():
            prediction = model(input_tensor).item()

        return jsonify({
            'item_id': item_id,
            'prediction': prediction
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500
