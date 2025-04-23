from flask import Blueprint, jsonify, send_file
from database.db_operations import get_all_predictions
from utils.export import export_to_csv, export_to_pdf

history_bp = Blueprint('history', __name__)

@history_bp.route('/api/history', methods=['GET'])
def get_history():
    predictions = get_all_predictions()
    return jsonify(predictions)

@history_bp.route('/api/history/export/csv', methods=['GET'])
def export_history_csv():
    predictions = get_all_predictions()
    filepath = export_to_csv(predictions)
    return send_file(filepath, as_attachment=True)

@history_bp.route('/api/history/export/pdf', methods=['GET'])
def export_history_pdf():
    predictions = get_all_predictions()
    filepath = export_to_pdf(predictions)
    return send_file(filepath, as_attachment=True)