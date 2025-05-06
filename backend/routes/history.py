from flask import Blueprint, request, jsonify
from backend.models.db_models import HistoryData

bp = Blueprint('history', __name__, url_prefix='/history')

@bp.route('', methods=['GET'])
def history():
    dept = request.args.get('dept')
    item_id = request.args.get('item_id')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    query = HistoryData.query
    if dept:
        query = query.filter_by(dept=dept)
    if item_id:
        query = query.filter_by(item_id=item_id)
    if start_date:
        query = query.filter(HistoryData.date >= start_date)
    if end_date:
        query = query.filter(HistoryData.date <= end_date)
    results = query.all()
    return jsonify([{'dept': r.dept, 'item_id': r.item_id, 'date': r.date, 'predicted_sales': r.predicted_sales} for r in results])