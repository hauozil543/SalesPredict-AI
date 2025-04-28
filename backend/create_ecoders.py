import sqlite3
import pickle

# Kết nối đến cơ sở dữ liệu
conn = sqlite3.connect('database/m5_forecasting.db')
cursor = conn.cursor()

# Lấy danh sách item_id duy nhất
cursor.execute("SELECT DISTINCT item_id FROM sales_data")
items = [row[0] for row in cursor.fetchall()]

# Lấy danh sách store_id duy nhất
cursor.execute("SELECT DISTINCT store_id FROM sales_data")
stores = [row[0] for row in cursor.fetchall()]

# Đóng kết nối
conn.close()

# Tạo encoder
item_encoder = {item: idx for idx, item in enumerate(items)}
store_encoder = {store: idx for idx, store in enumerate(stores)}

# Lưu encoder
with open('utils/item_encoder.pkl', 'wb') as f:
    pickle.dump(item_encoder, f)
with open('utils/store_encoder.pkl', 'wb') as f:
    pickle.dump(store_encoder, f)

print("Đã tạo item_encoder.pkl và store_encoder.pkl tại thư mục utils/")