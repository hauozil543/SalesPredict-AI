from flask import Blueprint, request, jsonify
from models.predictor import Predictor
from database.db_operations import get_historical_data
from utils.export import load_encoders, load_scaler

predict_bp = Blueprint('predict', __name__)

@predict_bp.route('/predict', methods=['POST'])
def predict_sales():
           # Lấy dữ liệu đầu vào từ request
           data = request.get_json()
           item_id = data.get('item_id')
           store_id = data.get('store_id')
           forecast_days = data.get('forecast_days')

           if not all([item_id, store_id, forecast_days]):
               return jsonify({'error': 'Missing required fields: item_id, store_id, forecast_days'}), 400

           try:
               forecast_days = int(forecast_days)
               if forecast_days <= 0:
                   raise ValueError
           except ValueError:
               return jsonify({'error': 'forecast_days must be a positive integer'}), 400

           # Tải encoders và scaler
           item_enc, store_enc = load_encoders()
           scaler = load_scaler()

           # Kiểm tra xem item_id và store_id có hợp lệ không
           try:
               item_idx = item_enc[item_id]
               store_idx = store_enc[store_id]
           except KeyError:
               return jsonify({'error': 'item_id or store_id not found in the trained dataset'}), 400

           # Lấy dữ liệu lịch sử từ processed_data.db
           historical_data = get_historical_data(item_idx, store_idx)
           if historical_data.empty:
               return jsonify({'error': 'No historical data found for the given item_id and store_id'}), 404

           # Khởi tạo predictor và thực hiện dự báo
           predictor = Predictor(model_path='model.pth', item_enc=item_enc, store_enc=store_enc, scaler=scaler)
           predictions = predictor.predict(historical_data, forecast_days)

           # Trả về kết quả dự báo
           return jsonify({
               'item_id': item_id,
               'store_id': store_id,
               'forecast_days': forecast_days,
               'predictions': predictions
           })      