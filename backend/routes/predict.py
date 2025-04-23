from flask import Blueprint, request, jsonify
from database.db_operations import insert_prediction
from models.predictor import Predictor

predict_bp = Blueprint('predict', __name__)
predictor = Predictor()

@predict_bp.route('/api/predict', methods=['POST'])
def predict():
    # Lấy dữ liệu JSON từ request
    data = request.get_json(silent=True)
    
    # Kiểm tra xem dữ liệu có hợp lệ không
    if data is None:
        return jsonify({
            'error': 'Invalid JSON or Content-Type not set to application/json'
        }), 400
    
    # Kiểm tra các khóa bắt buộc
    required_keys = ['X_num', 'X_item', 'X_store']
    missing_keys = [key for key in required_keys if key not in data]
    if missing_keys:
        return jsonify({
            'error': f'Missing required keys: {missing_keys}'
        }), 400
    
    # Giải nén dữ liệu
    try:
        X_num = data['X_num']
        X_item = data['X_item']
        X_store = data['X_store']
    except Exception as e:
        return jsonify({
            'error': f'Error unpacking data: {str(e)}'
        }), 400
    
    # Kiểm tra định dạng dữ liệu
    if not isinstance(X_num, list) or not all(isinstance(row, list) for row in X_num):
        return jsonify({
            'error': 'X_num must be a 2D list'
        }), 400
    if not isinstance(X_item, list) or not isinstance(X_store, list):
        return jsonify({
            'error': 'X_item and X_store must be lists'
        }), 400
    if len(X_num) != 28 or len(X_item) != 28 or len(X_store) != 28:
        return jsonify({
            'error': 'X_num, X_item, and X_store must each have length 28'
        }), 400
    
    # Thực hiện dự báo
    try:
        prediction = predictor.predict(X_num, X_item, X_store)
        input_data = {
            'X_num': X_num,
            'X_item': X_item,
            'X_store': X_store
        }
        insert_prediction(input_data, prediction)
        return jsonify({
            'prediction': prediction,
            'input_data': input_data
        }), 200
    except Exception as e:
        return jsonify({
            'error': f'Prediction failed: {str(e)}'
        }), 500