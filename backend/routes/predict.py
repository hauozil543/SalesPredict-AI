from flask import Blueprint, request, jsonify
import sqlite3
import pandas as pd
import numpy as np
import torch
import torch.nn as nn
from datetime import datetime, timedelta
import pickle
from flask_cors import CORS

# Định nghĩa đường dẫn cơ sở dữ liệu chung
DB_PATH = 'C:/Users/Ho Hau/Downloads/M5/backend/historical_data.db'

# Kiểm tra PyTorch và GPU
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

predict_bp = Blueprint('predict', __name__)

# Cấu hình CORS cho Blueprint
CORS(predict_bp, resources={r"/predict": {"origins": "http://localhost:5173"}})
CORS(predict_bp, resources={r"/history": {"origins": "http://localhost:5173"}})

# Định nghĩa mô hình LSTM
class LSTMModel(nn.Module):
    def __init__(self, input_size=12, hidden_size=128, num_layers=3, dropout=0.3):
        super(LSTMModel, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True, dropout=dropout)
        self.fc1 = nn.Linear(hidden_size, 32)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(32, 1)
        self.dropout = nn.Dropout(dropout)
    
    def forward(self, x):
        batch_size = x.size(0)
        h0 = torch.zeros(self.num_layers, batch_size, self.hidden_size).to(x.device)
        c0 = torch.zeros(self.num_layers, batch_size, self.hidden_size).to(x.device)
        
        out, _ = self.lstm(x, (h0, c0))
        out = self.dropout(out[:, -1, :])
        out = self.relu(self.fc1(out))
        out = self.fc2(out)
        return out

# Tải mô hình và scaler
model = LSTMModel(input_size=12).to(device)
model.load_state_dict(torch.load('C:/Users/Ho Hau/Downloads/M5/backend/lstm_model.pth', map_location=device))
model.eval()

with open('C:/Users/Ho Hau/Downloads/M5/backend/utils/scaler.pkl', 'rb') as f:
    scaler = pickle.load(f)

calendar = pd.read_csv('C:/Users/Ho Hau/Downloads/M5/data/raw/calendar.csv')
calendar['date'] = pd.to_datetime(calendar['date'])
TIME_STEPS = 28
NUM_FEATURES = 12
FEATURES = ['sales', 'sell_price', 'day_of_week', 'snap_CA', 'is_holiday', 'month', 'day_of_month',
            'sales_lag_7', 'sales_lag_14', 'sales_lag_28', 'sales_roll_mean_7', 'sales_roll_mean_14']

def get_historical_data(item_id, store_id, end_date):
    try:
        conn = sqlite3.connect(DB_PATH)
        query = '''SELECT date, sales, sell_price, day_of_week, snap_CA, is_holiday, month, day_of_month,
                          sales_lag_7, sales_lag_14, sales_lag_28, sales_roll_mean_7, sales_roll_mean_14
                   FROM historical_data
                   WHERE item_id = ? AND store_id = ? AND date <= ?
                   ORDER BY date DESC LIMIT 28'''
        df = pd.read_sql_query(query, conn, params=(item_id, store_id, end_date))
        conn.close()
        
        if len(df) < TIME_STEPS:
            print(f"Chỉ tìm thấy {len(df)} hàng cho {item_id} tại {store_id}, đang đệm thêm {TIME_STEPS - len(df)} hàng...")
            padding = pd.DataFrame(np.zeros((TIME_STEPS - len(df), len(FEATURES))), columns=FEATURES)
            end_date_dt = pd.to_datetime(end_date)
            padding_dates = [end_date_dt - pd.Timedelta(days=i) for i in range(len(df), TIME_STEPS)]
            padding['date'] = padding_dates[::-1]
            df = pd.concat([padding, df], ignore_index=True)
        
        return df
    except Exception as e:
        print(f"Error in get_historical_data: {str(e)}")
        raise

def calculate_rolling_mean(data, window):
    if len(data) < window:
        return 0
    return np.mean(data[-window:])

@predict_bp.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        required_keys = ['item_id', 'store_id', 'start_date', 'end_date']
        for key in required_keys:
            if key not in data:
                return jsonify({'error': f'Thiếu "{key}" trong dữ liệu gửi lên'}), 400
        
        item_id = data['item_id']
        store_id = data['store_id']
        start_date = datetime.strptime(data['start_date'], '%Y-%m-%d')
        end_date = datetime.strptime(data['end_date'], '%Y-%m-%d')
        
        if start_date > end_date:
            return jsonify({'error': 'start_date phải trước end_date'}), 400

        seq_end_date = (start_date - timedelta(days=1)).strftime('%Y-%m-%d')
        historical_df = get_historical_data(item_id, store_id, seq_end_date)
        historical_df = historical_df.sort_values('date')
        print(f"Historical data date range: {historical_df['date'].min()} to {historical_df['date'].max()}")
        
        historical_data = historical_df[FEATURES].values
        sales_history = historical_df['sales'].tolist()
        
        num_days = (end_date - start_date).days + 1
        current_historical_data = historical_data.copy()
        predictions = []
        current_date = start_date
        
        for i in range(num_days):
            input_data = np.array([current_historical_data], dtype=np.float32)
            input_tensor = torch.tensor(input_data, dtype=torch.float32).to(device)
            
            with torch.no_grad():
                prediction_scaled = model(input_tensor).cpu().numpy().squeeze()
            
            dummy_array = np.zeros((1, NUM_FEATURES))
            dummy_array[0, 0] = prediction_scaled
            prediction = scaler.inverse_transform(dummy_array)[0, 0]
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            c.execute('''INSERT INTO predictions (item_id, store_id, date, prediction, timestamp)
                         VALUES (?, ?, ?, ?, ?)''',
                      (item_id, store_id, current_date.strftime('%Y-%m-%d'), float(prediction), timestamp))
            conn.commit()
            conn.close()
            
            predictions.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'prediction': float(prediction)
            })
            
            new_row = np.zeros(NUM_FEATURES)
            new_row[0] = prediction_scaled
            
            current_date_obj = pd.to_datetime(current_date)
            new_row[2] = current_date_obj.dayofweek / 6.0
            new_row[5] = current_date_obj.month / 12.0
            new_row[6] = current_date_obj.day / 31.0
            
            calendar_row = calendar[calendar['date'] == pd.to_datetime(current_date)]
            if not calendar_row.empty:
                snap_ca = calendar_row['snap_CA'].values[0]
                is_holiday = 1 if pd.notnull(calendar_row['event_name_1'].values[0]) or pd.notnull(calendar_row['event_name_2'].values[0]) else 0
                print(f"Date {current_date.strftime('%Y-%m-%d')}: snap_CA={snap_ca}, is_holiday={is_holiday}")
            else:
                snap_ca = 0
                is_holiday = 0
                print(f"Date {current_date.strftime('%Y-%m-%d')}: No calendar data found, setting snap_CA=0, is_holiday=0")
            
            new_row[3] = snap_ca
            new_row[4] = is_holiday
            new_row[1] = current_historical_data[-1, 1]
            
            sales_history.append(prediction_scaled)
            new_row[7] = sales_history[-7] if len(sales_history) >= 7 else 0
            new_row[8] = sales_history[-14] if len(sales_history) >= 14 else 0
            new_row[9] = sales_history[-28] if len(sales_history) >= 28 else 0
            new_row[10] = calculate_rolling_mean(sales_history, 7)
            new_row[11] = calculate_rolling_mean(sales_history, 14)
            
            print(f"Date {current_date.strftime('%Y-%m-%d')}: day_of_week={new_row[2]*6.0:.1f}, month={new_row[5]*12.0:.1f}, day_of_month={new_row[6]*31.0:.1f}, snap_CA={new_row[3]}, is_holiday={new_row[4]}")
            
            current_historical_data = np.vstack((current_historical_data[1:], new_row))
            current_date += timedelta(days=1)
        
        return jsonify({
            'predictions': predictions,
            'status': 'success'
        }), 200
    
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@predict_bp.route('/history', methods=['GET'])
def get_history():
    try:
        # Lấy các tham số từ query string
        limit = request.args.get('limit', default=50, type=int)
        item_id = request.args.get('item_id', default=None, type=str)
        store_id = request.args.get('store_id', default=None, type=str)
        start_date = request.args.get('start_date', default=None, type=str)
        end_date = request.args.get('end_date', default=None, type=str)

        # Kiểm tra định dạng ngày nếu có
        if start_date:
            try:
                datetime.strptime(start_date, '%Y-%m-%d')
            except ValueError:
                return jsonify({'error': 'start_date phải có định dạng YYYY-MM-DD'}), 400
        if end_date:
            try:
                datetime.strptime(end_date, '%Y-%m-%d')
            except ValueError:
                return jsonify({'error': 'end_date phải có định dạng YYYY-MM-DD'}), 400

        if start_date and end_date:
            if datetime.strptime(start_date, '%Y-%m-%d') > datetime.strptime(end_date, '%Y-%m-%d'):
                return jsonify({'error': 'start_date phải trước end_date'}), 400

        # Truy vấn dữ liệu từ bảng predictions
        query = '''SELECT id, item_id, store_id, date, prediction, timestamp
                   FROM predictions
                   WHERE (? IS NULL OR item_id = ?)
                   AND (? IS NULL OR store_id = ?)
                   AND (? IS NULL OR date >= ?)
                   AND (? IS NULL OR date <= ?)
                   ORDER BY timestamp DESC, date ASC'''
        params = (item_id, item_id, store_id, store_id, start_date, start_date, end_date, end_date)

        print(f"Attempting to connect to合作 at: {DB_PATH}")
        conn = sqlite3.connect(DB_PATH)
        print("Database connection successful for get_history")
        c = conn.cursor()
        c.execute(query, params)
        rows = c.fetchall()
        conn.close()

        # Nhóm dữ liệu theo timestamp
        history_by_timestamp = {}
        for row in rows:
            timestamp = row[5]  # Cột timestamp
            if timestamp not in history_by_timestamp:
                history_by_timestamp[timestamp] = []
            history_by_timestamp[timestamp].append({
                'id': row[0],
                'item_id': row[1],
                'store_id': row[2],
                'date': row[3],
                'prediction': float(row[4])
            })

        # Chuyển đổi thành định dạng yêu cầu
        forecast_history = []
        stt = 1
        for timestamp in sorted(history_by_timestamp.keys(), reverse=True):
            forecasts = history_by_timestamp[timestamp]
            forecast_entry = {
                'stt': stt,
                'timestamp': timestamp,
                'forecasts': forecasts
            }
            forecast_history.append(forecast_entry)
            stt += 1

        forecast_history = forecast_history[:limit]

        if not forecast_history:
            return jsonify({'message': 'Không tìm thấy dữ liệu phù hợp', 'forecast_history': [], 'status': 'success'}), 200

        return jsonify({
            'forecast_history': forecast_history,
            'status': 'success'
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500