from flask import Blueprint, jsonify, request
import psycopg2
from psycopg2 import sql, errors

home_bp = Blueprint('/', __name__)

# Cấu hình kết nối PostgreSQL
DB_CONFIG = {
    'dbname': 'm5_data',
    'user': 'postgres',
    'password': 'H30012003h',
    'host': 'localhost',
    'port': '5432'
}

def get_db_connection():
    """Tạo kết nối đến PostgreSQL."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except errors.OperationalError as e:
        print(f"Lỗi kết nối database: {e}")
        raise Exception(f"Không thể kết nối đến database: {str(e)}")

def apply_filters(query, params, table_prefix='s'):
    """Hàm hỗ trợ thêm điều kiện lọc vào truy vấn SQL."""
    conditions = []
    values = []
    if 'state' in params:
        conditions.append(f"{table_prefix}.state_id = %s")
        values.append(params['state'])
    if 'store_id' in params:
        conditions.append(f"{table_prefix}.store_id = %s")
        values.append(params['store_id'])
    if 'startDate' in params and 'endDate' in params:
        conditions.append("c.date BETWEEN %s AND %s")
        values.extend([params['startDate'], params['endDate']])
    elif 'startDate' in params:
        conditions.append("c.date >= %s")
        values.append(params['startDate'])
    elif 'endDate' in params:
        conditions.append("c.date <= %s")
        values.append(params['endDate'])
    # Chỉ thêm điều kiện mặc định nếu không có startDate hoặc endDate
    if not ('startDate' in params or 'endDate' in params):
        conditions.append("c.date BETWEEN '2016-01-01' AND '2016-04-24'")
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    return query, tuple(values)

@home_bp.route('/dashboard', methods=['GET'])
def get_dashboard():
    params = request.args.to_dict()
    print(f"Params in /dashboard: {params}")
    try:
        conn = get_db_connection()
        c = conn.cursor()

        # Tổng quan
        overview_query = """
            SELECT 
                COALESCE(SUM(s.sales * p.sell_price), 0) as total_revenue,
                (
                    SELECT COALESCE(SUM(s2.sales), 0)
                    FROM sales s2
                    LEFT JOIN calendar c ON s2.d_id = c.d_id
                    LEFT JOIN prices p2 ON s2.item_id = p2.item_id AND s2.store_id = p2.store_id AND c.wm_yr_wk = p2.wm_yr_wk
                    %s
                ) as total_products_sold_by_store,
                COUNT(DISTINCT REGEXP_REPLACE(s.item_id, '[0-9]+$', '')) as total_product_categories
            FROM sales s
            LEFT JOIN calendar c ON s.d_id = c.d_id
            LEFT JOIN prices p ON s.item_id = p.item_id AND s.store_id = p.store_id AND c.wm_yr_wk = p.wm_yr_wk
        """
        # Áp dụng điều kiện lọc cho subquery (với table_prefix='s2')
        subquery, subquery_values = apply_filters("", params, table_prefix='s2')
        overview_query = overview_query % subquery
        # Áp dụng điều kiện lọc cho outer query (với table_prefix='s')
        overview_query, overview_values = apply_filters(overview_query, params, table_prefix='s')
        print(f"Overview Query: {overview_query}, Values: {overview_values + subquery_values}")
        c.execute(overview_query, overview_values + subquery_values)
        overview_row = c.fetchone()

        # Doanh thu theo ngày
        sales_by_date_query = """
            SELECT 
                c.date, COALESCE(SUM(s.sales * p.sell_price), 0) as daily_revenue
            FROM sales s
            LEFT JOIN calendar c ON s.d_id = c.d_id
            LEFT JOIN prices p ON s.item_id = p.item_id AND s.store_id = p.store_id AND c.wm_yr_wk = p.wm_yr_wk
        """
        sales_by_date_query, sales_by_date_values = apply_filters(sales_by_date_query, params)
        sales_by_date_query += " GROUP BY c.date ORDER BY c.date"
        print(f"Sales by Date Query: {sales_by_date_query}, Values: {sales_by_date_values}")
        c.execute(sales_by_date_query, sales_by_date_values)
        sales_by_date_rows = c.fetchall()

        # Top 10 sản phẩm (doanh thu theo sản phẩm)
        top_products_query = """
            SELECT 
                s.item_id, COALESCE(SUM(s.sales * p.sell_price), 0) as product_revenue
            FROM sales s
            LEFT JOIN calendar c ON s.d_id = c.d_id
            LEFT JOIN prices p ON s.item_id = p.item_id AND s.store_id = p.store_id AND c.wm_yr_wk = p.wm_yr_wk
        """
        top_products_query, top_products_values = apply_filters(top_products_query, params)
        top_products_query += " GROUP BY s.item_id HAVING SUM(COALESCE(s.sales * p.sell_price, 0)) > 0 ORDER BY product_revenue DESC LIMIT 10"
        print(f"Top Products Query: {top_products_query}, Values: {top_products_values}")
        c.execute(top_products_query, top_products_values)
        top_products_rows = c.fetchall()

        return jsonify({
            "overview": {
                "total_revenue": float(overview_row[0]) if overview_row[0] else 0,
                "total_products_sold_by_store": overview_row[1] if overview_row[1] else 0,
                "total_product_categories": overview_row[2] if overview_row[2] else 0
            },
            "sales_by_date": [{"date": str(row[0]), "revenue": float(row[1]) if row[1] else 0} for row in sales_by_date_rows],
            "top_products": [{"item_id": row[0], "product_revenue": float(row[1]) if row[1] else 0} for row in top_products_rows]
        })
    except Exception as e:
        print(f"Lỗi trong /dashboard: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        if 'conn' in locals():
            conn.close()

@home_bp.route('/dates', methods=['GET'])
def get_dates():
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT DISTINCT date FROM calendar WHERE date BETWEEN '2016-01-01' AND '2016-04-24' ORDER BY date")
        rows = c.fetchall()
        return jsonify([str(row[0]) for row in rows])
    except Exception as e:
        print(f"Lỗi trong /dates: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        if 'conn' in locals():
            conn.close()