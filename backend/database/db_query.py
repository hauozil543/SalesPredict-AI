import sqlite3

# Kết nối đến cơ sở dữ liệu SQLite
conn = sqlite3.connect("m5_forecasting.db")
cursor = conn.cursor()

# Truy vấn và hiển thị dữ liệu
cursor.execute("SELECT * FROM normalized_train_data LIMIT 10;")
rows = cursor.fetchall()
for row in rows:
    print(row)

# Đóng kết nối
conn.close()
