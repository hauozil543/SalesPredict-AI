from flask import Blueprint, jsonify
import sqlite3
import pandas as pd
import os

items_bp = Blueprint('items', __name__)

db_path = os.path.join(os.getcwd(), 'backend', 'database', 'm5_forecasting.db')

@items_bp.route('/api/items', methods=['GET'])
def get_items():
    try:
        conn = sqlite3.connect(db_path)
        query = "SELECT DISTINCT item_id FROM sales_long"
        df = pd.read_sql(query, conn)
        conn.close()
        return jsonify(df['item_id'].tolist())
    except Exception as e:
        return jsonify({"error": str(e)}), 500
