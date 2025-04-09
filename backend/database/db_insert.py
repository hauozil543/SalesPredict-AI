import sqlite3
import pandas as pd
import os

# Đảm bảo đường dẫn tới file CSV là chính xác
file_path = 'C:/Users/Ho Hau/Downloads/M5/backend/database/train_data_normalized.csv'

# Đọc dữ liệu từ file CSV
df_normalized = pd.read_csv(file_path)

# Kết nối đến cơ sở dữ liệu SQLite
conn = sqlite3.connect("m5_forecasting.db")

# Chèn dữ liệu vào bảng normalized_train_data
df_normalized.to_sql("normalized_train_data", conn, if_exists="replace", index=False)

# Đóng kết nối
conn.close()

print("✅ Dữ liệu đã được nhập vào SQLite thành công!")
