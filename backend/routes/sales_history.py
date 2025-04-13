from flask import Blueprint, request, jsonify
import sqlite3
import pandas as pd
import os

sales_history_bp = Blueprint('sales_history', __name__)

db_path = os.path.join(os.getcwd(), 'backend', 'database', 'm5_forecasting.db')

@sales_history_bp.route('/api/sales-history', methods=['GET'])
def get_sales_history():
    item_id = request.args.get('item_id')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    if not item_id or not start_date or not end_date:
        return jsonify({"error": "Missing parameters"}), 400

    try:
        conn = sqlite3.connect(db_path)
        query = """
            SELECT day, value
            FROM sales_long
            WHERE item_id = ? AND day BETWEEN ? AND ?
            ORDER BY day
        """
        df = pd.read_sql(query, conn, params=(item_id, start_date, end_date))
        conn.close()
        return jsonify(df.to_dict(orient='records'))
    except Exception as e:
        return jsonify({"error": str(e)}), 500
