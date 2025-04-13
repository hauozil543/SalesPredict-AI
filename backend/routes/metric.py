from flask import Blueprint, jsonify

metrics_bp = Blueprint('metrics', __name__)

# Giả sử bạn đã tính toán trước và lưu trong file
@metrics_bp.route('/api/metrics', methods=['GET'])
def get_metrics():
    try:
        metrics = {
            "MAE": 0.214,
            "RMSE": 0.389,
            "MAPE": 0.126
        }
        return jsonify(metrics)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
