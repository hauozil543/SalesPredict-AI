from flask import Blueprint, jsonify, request
import sqlite3

# Tạo Blueprint cho API chart
chart_bp = Blueprint('chart_bp', __name__)

DATABASE = "m5_forecasting.db"  # Đường dẫn tới cơ sở dữ liệu

# Kết nối với cơ sở dữ liệu SQLite
def get_db():
    conn = sqlite3.connect(DATABASE)
    return conn

# API để lấy dữ liệu biểu đồ
@chart_bp.route('/', methods=['GET'])
def get_chart_data():
    try:
        # Lấy tham số từ URL
        item_id = request.args.get('item_id')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Kết nối với cơ sở dữ liệu
        conn = get_db()
        cursor = conn.cursor()
        
        # Truy vấn dữ liệu từ bảng sales_long
        cursor.execute("""
            SELECT date, sales FROM sales_long
            WHERE item_store_id = ? AND date BETWEEN ? AND ?
        """, (item_id, start_date, end_date))
        
        # Lấy dữ liệu và chuyển đổi thành định dạng JSON
        sales_data = cursor.fetchall()
        result = [{"date": row[0], "sales": row[1]} for row in sales_data]
        
        # Trả về kết quả dưới dạng JSON
        return jsonify(result)
    except Exception as e:
        # Xử lý lỗi nếu có
        return jsonify({"error": str(e)}), 500
    finally:
        # Đảm bảo đóng kết nối với cơ sở dữ liệu
        conn.close()
