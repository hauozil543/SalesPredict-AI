import sqlite3

def connect_db():
    conn = sqlite3.connect("m5_forecasting.db")  # Tạo hoặc kết nối database
    conn.row_factory = sqlite3.Row  # Giúp truy xuất dữ liệu dễ dàng hơn
    return conn
