from flask import Blueprint, request, jsonify
from models.predictor import Predictor
from database.db_operations import insert_prediction

predict_bp = Blueprint('predict', __name__)
predictor = Predictor()

@predict_bp.route('/api/predict', methods=['POST'])
def predict():
    data = request.get_json()
    # Giả định dữ liệu đầu vào
    X_num = data['X_num']  # (28, num_features)
    X_item = data['X_item']  # (28,)
    X_store = data['X_store']  # (28,)

    # Dự báo
    prediction = predictor.predict(X_num, X_item, X_store)

    # Lưu vào database
    input_data = {
        'X_num': X_num,
        'X_item': X_item,
        'X_store': X_store
    }
    insert_prediction(input_data, prediction)

    return jsonify({
        'prediction': prediction,
        'input_data': input_data
    })