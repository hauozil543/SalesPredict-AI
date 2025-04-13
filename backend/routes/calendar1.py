from flask import Blueprint, jsonify
import sqlite3
import pandas as pd
import os

calendar_bp = Blueprint('calendar', __name__)

db_path = os.path.join(os.getcwd(), 'backend', 'database', 'm5_forecasting.db')

@calendar_bp.route('/api/calendar', methods=['GET'])
def get_calendar():
    try:
        conn = sqlite3.connect(db_path)
        df = pd.read_sql("SELECT * FROM calendar", conn)
        conn.close()
        return jsonify(df.to_dict(orient='records'))
    except Exception as e:
        return jsonify({"error": str(e)}), 500
