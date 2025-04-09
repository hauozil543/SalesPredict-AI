import sqlite3

conn = sqlite3.connect("m5_forecasting.db")
cursor = conn.cursor()

# Tạo bảng trong cơ sở dữ liệu
cursor.execute('''
    CREATE TABLE IF NOT EXISTS normalized_train_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        normalized_value REAL
    )
''')

conn.commit()
conn.close()
print("✅ Database và bảng normalized_train_data đã được tạo thành công!")
