from flask import Blueprint, jsonify, request
import psycopg2
from psycopg2 import sql

home_bp = Blueprint('/', __name__)

# Cấu hình kết nối PostgreSQL
DB_CONFIG = {
    'dbname': 'm5_data',
    'user': 'postgres',
    'password': 'H30012003h',  
    'port': '5432'
}

def get_db_connection():
    """Tạo kết nối đến PostgreSQL."""
    return psycopg2.connect(**DB_CONFIG)

def apply_filters(query, params):
    """Hàm hỗ trợ thêm điều kiện lọc vào truy vấn SQL."""
    conditions = []
    if 'state' in params:
        conditions.append("state_id = %s")
    if 'store_id' in params:
        conditions.append("store_id = %s")
    if 'date' in params:
        conditions.append("date = %s")
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
        if "sales IS NOT NULL AND sell_price IS NOT NULL" not in query:
            query += " AND sales IS NOT NULL AND sell_price IS NOT NULL"
    else:
        query += " WHERE sales IS NOT NULL AND sell_price IS NOT NULL"
    return query, tuple(params.get(key) for key in ['state', 'store_id', 'date'] if key in params)

@home_bp.route('/overview', methods=['GET'])
def get_overview():
    params = request.args.to_dict()
    conn = get_db_connection()
    c = conn.cursor()
    
    query = """
        SELECT SUM(sales * sell_price) as total_revenue,
               COUNT(DISTINCT item_id) as total_products,
               COUNT(DISTINCT store_id) as total_stores
        FROM sales_raw
    """
    query, values = apply_filters(query, params)
    
    c.execute(query, values)
    row = c.fetchone()
    conn.close()
    return jsonify({
        "total_revenue": float(row[0]) if row[0] is not None else 0,
        "total_products_sold": row[1],
        "total_stores": row[2]
    })

@home_bp.route('/sales_by_date', methods=['GET'])
def sales_by_date():
    params = request.args.to_dict()
    conn = get_db_connection()
    c = conn.cursor()
    
    query = """
        SELECT date, SUM(sales * sell_price) as daily_revenue
        FROM sales_raw
    """
    query, values = apply_filters(query, params)
    query += " GROUP BY date ORDER BY date"
    
    c.execute(query, values)
    rows = c.fetchall()
    conn.close()
    return jsonify([{"date": str(row[0]), "revenue": float(row[1]) if row[1] is not None else 0} for row in rows])

@home_bp.route('/top_products', methods=['GET'])
def top_products():
    params = request.args.to_dict()
    conn = get_db_connection()
    c = conn.cursor()
    
    query = """
        SELECT item_id, SUM(sales * sell_price) as total_revenue
        FROM sales_raw
    """
    query, values = apply_filters(query, params)
    query += " GROUP BY item_id ORDER BY total_revenue DESC LIMIT 10"
    
    c.execute(query, values)
    rows = c.fetchall()
    conn.close()
    return jsonify([{"item_id": row[0], "total_revenue": float(row[1]) if row[1] is not None else 0} for row in rows])

@home_bp.route('/sales_by_store', methods=['GET'])
def sales_by_store():
    params = request.args.to_dict()
    conn = get_db_connection()
    c = conn.cursor()
    
    query = """
        SELECT store_id, SUM(sales * sell_price) as total_revenue
        FROM sales_raw
    """
    query, values = apply_filters(query, params)
    query += " GROUP BY store_id"
    
    c.execute(query, values)
    rows = c.fetchall()
    conn.close()
    return jsonify([{"store_id": row[0], "total_revenue": float(row[1]) if row[1] is not None else 0} for row in rows])

@home_bp.route('/states', methods=['GET'])
def get_states():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT DISTINCT state_id FROM sales_raw ORDER BY state_id")
    rows = c.fetchall()
    conn.close()
    return jsonify([row[0] for row in rows])

@home_bp.route('/stores', methods=['GET'])
def get_stores():
    params = request.args.to_dict()
    conn = get_db_connection()
    c = conn.cursor()
    query = "SELECT DISTINCT store_id FROM sales_raw"
    if 'state' in params:
        query += " WHERE state_id = %s"
        c.execute(query, (params['state'],))
    else:
        c.execute(query)
    rows = c.fetchall()
    conn.close()
    return jsonify([row[0] for row in rows])

@home_bp.route('/dates', methods=['GET'])
def get_dates():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT DISTINCT date FROM sales_raw ORDER BY date")
    rows = c.fetchall()
    conn.close()
    return jsonify([str(row[0]) for row in rows])