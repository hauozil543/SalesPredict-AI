import sqlite3

# Đường dẫn đến cơ sở dữ liệu
DB_PATH = 'C:/Users/Ho Hau/Downloads/M5/backend/historical_data.db'

try:
    # Kết nối đến cơ sở dữ liệu
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Truy vấn danh sách các bảng
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    # In danh sách các bảng
    if tables:
        print("Các bảng trong cơ sở dữ liệu historical_data.db:")
        for table in tables:
            print(f"- {table[0]}")
    else:
        print("Không tìm thấy bảng nào trong cơ sở dữ liệu.")

    # Đóng kết nối
    conn.close()

except sqlite3.Error as e:
    print(f"Lỗi khi truy vấn cơ sở dữ liệu: {e}")