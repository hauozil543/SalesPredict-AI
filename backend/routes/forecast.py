from flask import Blueprint, request, jsonify
from models.predict import predict_sales

forecast_bp = Blueprint('forecast', __name__)

@forecast_bp.route('/predict', methods=['POST'])
def get_forecast():
    try:
        data = request.json
        features = data["features"]
        
        prediction = predict_sales(features)
        return jsonify({"prediction": prediction})

    except Exception as e:
        return jsonify({"error": str(e)})