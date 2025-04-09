from flask import Flask, jsonify, request
import sqlite3
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Cấu hình CORS để frontend có thể kết nối

DATABASE = "m5_forecasting.db"  # Đường dẫn tới cơ sở dữ liệu

def get_db():
    conn = sqlite3.connect(DATABASE)
    return conn

@app.route('/items', methods=['GET'])
def get_items():
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT item_store_id FROM sales_long")
        items = cursor.fetchall()
        item_list = [item[0] for item in items]  # Chuyển đổi tuple thành list
        return jsonify(item_list)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@app.route('/chart', methods=['GET'])
def get_chart_data():
    try:
        item_id = request.args.get('item_id')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT date, sales FROM sales_long
            WHERE item_store_id = ? AND date BETWEEN ? AND ?
        """, (item_id, start_date, end_date))
        
        sales_data = cursor.fetchall()
        result = [{"date": row[0], "sales": row[1]} for row in sales_data]  # Định dạng lại dữ liệu
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)
