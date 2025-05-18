from flask import Blueprint, jsonify, request
import psycopg2
from psycopg2 import pool, errors
import time

home_bp = Blueprint('/', __name__)

# Cấu hình connection pool
DB_CONFIG = {
    'dbname': 'm5_data',
    'user': 'postgres',
    'password': 'H30012003h',
    'host': 'localhost',
    'port': '5432'
}
db_pool = psycopg2.pool.SimpleConnectionPool(1, 20, **DB_CONFIG)

def get_db_connection():
    """Tạo kết nối đến PostgreSQL từ pool."""
    try:
        return db_pool.getconn()
    except errors.OperationalError as e:
        print(f"Lỗi kết nối database: {e}")
        raise Exception(f"Không thể kết nối đến database: {str(e)}")

def release_db_connection(conn):
    """Trả kết nối về pool."""
    db_pool.putconn(conn)

def apply_filters(params, table_prefix='s'):
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
    if not ('startDate' in params or 'endDate' in params):
        conditions.append("c.date BETWEEN '2016-01-01' AND '2016-04-24'")
    conditions.append(f"{table_prefix}.sales > 0")  # Loại bỏ sớm các hàng không có doanh số
    return conditions, values

@home_bp.route('/dashboard', methods=['GET'])
def get_dashboard():
    params = request.args.to_dict()
    print(f"Params in /dashboard: {params}")
    conn = None
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
                    WHERE %s
                ) as total_products_sold_by_store,
                COUNT(DISTINCT REGEXP_REPLACE(s.item_id, '[0-9]+$', '')) as total_product_categories
            FROM sales s
            LEFT JOIN calendar c ON s.d_id = c.d_id
            LEFT JOIN prices p ON s.item_id = p.item_id AND s.store_id = p.store_id AND c.wm_yr_wk = p.wm_yr_wk
            WHERE %s
        """
        # Lấy điều kiện và giá trị cho subquery
        subquery_conditions, subquery_values = apply_filters(params, table_prefix='s2')
        subquery_where = " AND ".join(subquery_conditions) if subquery_conditions else "TRUE"
        
        # Lấy điều kiện và giá trị cho truy vấn chính
        main_conditions, main_values = apply_filters(params, table_prefix='s')
        main_where = " AND ".join(main_conditions) if main_conditions else "TRUE"
        
        # Chèn điều kiện vào truy vấn
        final_query = overview_query % (subquery_where, main_where)
        
        # Kết hợp tất cả giá trị
        all_values = subquery_values + main_values
        print(f"Overview Query: {final_query}, Values: {all_values}")
        start_time = time.time()
        c.execute(final_query, all_values)
        overview_row = c.fetchone()
        print(f"Overview query took {time.time() - start_time:.2f} seconds")

        # Doanh thu theo ngày
        sales_by_date_query = """
            SELECT 
                c.date, COALESCE(SUM(s.sales * p.sell_price), 0) as daily_revenue
            FROM sales s
            INNER JOIN calendar c ON s.d_id = c.d_id
            INNER JOIN prices p ON s.item_id = p.item_id AND s.store_id = p.store_id AND c.wm_yr_wk = p.wm_yr_wk
        """
        conditions, values = apply_filters(params)
        where_clause = " AND ".join(conditions) if conditions else ""
        if where_clause:
            sales_by_date_query += f" WHERE {where_clause}"
        sales_by_date_query += " GROUP BY c.date ORDER BY c.date"
        print(f"Sales by Date Query: {sales_by_date_query}, Values: {values}")
        start_time = time.time()
        c.execute(sales_by_date_query, values)
        sales_by_date_rows = c.fetchall()
        print(f"Sales by date query took {time.time() - start_time:.2f} seconds")

        # Top 10 sản phẩm dựa trên tổng số sản phẩm bán được
        top_products_query = """
            SELECT 
                s.item_id, COALESCE(SUM(s.sales), 0) as total_sales
            FROM sales s
            INNER JOIN calendar c ON s.d_id = c.d_id
            INNER JOIN prices p ON s.item_id = p.item_id AND s.store_id = p.store_id AND c.wm_yr_wk = p.wm_yr_wk
        """
        conditions, values = apply_filters(params)
        where_clause = " AND ".join(conditions) if conditions else ""
        if where_clause:
            top_products_query += f" WHERE {where_clause}"
        top_products_query += " GROUP BY s.item_id HAVING SUM(COALESCE(s.sales, 0)) > 0 ORDER BY total_sales DESC LIMIT 10"
        print(f"Top Products Query: {top_products_query}, Values: {values}")
        start_time = time.time()
        c.execute(top_products_query, values)
        top_products_rows = c.fetchall()
        print(f"Top products query took {time.time() - start_time:.2f} seconds")

        # Tỷ lệ doanh số theo loại sản phẩm (lấy tối đa 7 loại)
        product_categories_query = """
            SELECT 
                REGEXP_REPLACE(s.item_id, '[0-9]+$', '') as category,
                COALESCE(SUM(s.sales), 0) as total_sales
            FROM sales s
            INNER JOIN calendar c ON s.d_id = c.d_id
            INNER JOIN prices p ON s.item_id = p.item_id AND s.store_id = p.store_id AND c.wm_yr_wk = p.wm_yr_wk
        """
        conditions, values = apply_filters(params)
        where_clause = " AND ".join(conditions) if conditions else ""
        if where_clause:
            product_categories_query += f" WHERE {where_clause}"
        product_categories_query += " GROUP BY category ORDER BY total_sales DESC LIMIT 7"
        print(f"Product Categories Query: {product_categories_query}, Values: {values}")
        start_time = time.time()
        c.execute(product_categories_query, values)
        product_categories_rows = c.fetchall()
        print(f"Product categories query took {time.time() - start_time:.2f} seconds")
        print(f"Product Categories Data: {product_categories_rows}")

        return jsonify({
            "overview": {
                "total_revenue": float(overview_row[0]) if overview_row[0] else 0,
                "total_products_sold_by_store": overview_row[1] if overview_row[1] else 0,
                "total_product_categories": overview_row[2] if overview_row[2] else 0
            },
            "sales_by_date": [{"date": str(row[0]), "revenue": float(row[1]) if row[1] else 0} for row in sales_by_date_rows],
            "top_products": [{"item_id": row[0], "total_sales": int(row[1]) if row[1] else 0} for row in top_products_rows],
            "product_categories": [{"category": row[0], "total_sales": int(row[1]) if row[1] else 0} for row in product_categories_rows]
        })
    except Exception as e:
        print(f"Lỗi trong /dashboard: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            release_db_connection(conn)

@home_bp.route('/dates', methods=['GET'])
def get_dates():
    conn = None
    try:
        conn = get_db_connection()
        c = conn.cursor()
        start_time = time.time()
        c.execute("SELECT DISTINCT date FROM calendar WHERE date BETWEEN '2016-01-01' AND '2016-04-24' ORDER BY date")
        rows = c.fetchall()
        print(f"Dates query took {time.time() - start_time:.2f} seconds")
        return jsonify([str(row[0]) for row in rows])
    except Exception as e:
        print(f"Lỗi trong /dates: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            release_db_connection(conn)