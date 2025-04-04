from flask import Blueprint, request, jsonify
import torch
import numpy as np
import pandas as pd
from models.lstm_model import LSTMModel
from database.db_connecttion import get_db_connection  # Hàm kết nối database

forecast_bp = Blueprint('forecast', __name__)

# Load mô hình LSTM
MODEL_PATH = "lstm_model.pth"
input_size = 1
hidden_size = 512
output_size = 1
model = LSTMModel(input_size, hidden_size, output_size)
model.load_state_dict(torch.load(MODEL_PATH, map_location=torch.device("cpu")))
model.eval()

# Hàm lấy dữ liệu lịch sử từ database
def get_historical_data(start_date, days=30):
    conn = get_db_connection()
    query = f"""
        SELECT date, sales FROM sales_data
        WHERE date >= DATEADD(day, -{days}, '{start_date}')
        AND date < '{start_date}'
        ORDER BY date ASC
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# API dự báo theo khoảng thời gian
@forecast_bp.route('/predict-range', methods=['POST'])
def predict_range():
    try:
        data = request.json
        start_date = data.get("start_date")
        end_date = data.get("end_date")
        
        # Lấy dữ liệu lịch sử
        historical_df = get_historical_data(start_date)
        if historical_df.empty:
            return jsonify({"error": "Không có dữ liệu lịch sử đủ để dự báo"}), 400
        
        # Chuẩn bị dữ liệu đầu vào
        features = historical_df["sales"].values.astype(np.float32)
        input_tensor = torch.tensor(features).unsqueeze(0)  # Định dạng batch
        
        predictions = []
        current_input = input_tensor.clone()
        
        # Lặp qua từng ngày trong khoảng dự báo
        num_days = (pd.to_datetime(end_date) - pd.to_datetime(start_date)).days + 1
        for _ in range(num_days):
            with torch.no_grad():
                pred = model(current_input).item()
            predictions.append(pred)
            
            # Cập nhật đầu vào cho ngày tiếp theo
            current_input = torch.cat((current_input[:, 1:], torch.tensor([[pred]])), dim=1)
        
        # Tạo danh sách kết quả
        prediction_dates = pd.date_range(start=start_date, periods=num_days).strftime('%Y-%m-%d').tolist()
        result = [{"date": d, "sales": s} for d, s in zip(prediction_dates, predictions)]
        
        return jsonify({"predictions": result})
    
    except Exception as e:
        return jsonify({"error": str(e)})
