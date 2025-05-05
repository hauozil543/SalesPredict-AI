import pandas as pd
from sqlalchemy import create_engine, text
import os

# Cấu hình kết nối PostgreSQL
DB_CONFIG = {
    'dbname': 'm5_data',
    'user': 'postgres',
    'password': 'H30012003h',
    'host': 'localhost',
    'port': '5432'
}

try:
    # Kết nối PostgreSQL
    print("Đang kết nối đến PostgreSQL...")
    engine = create_engine(f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['dbname']}")
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        print("Kết nối thành công! Kết quả kiểm tra:", result.fetchone()[0])

    # Đường dẫn đến file dữ liệu
    data_dir = 'C:/Users/Ho Hau/Downloads/M5/data/raw/'
    sales_file = os.path.join(data_dir, 'sales_train_validation.csv')
    calendar_file = os.path.join(data_dir, 'calendar.csv')
    prices_file = os.path.join(data_dir, 'sell_prices.csv')

    # Kiểm tra file tồn tại
    for file_path in [sales_file, calendar_file, prices_file]:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File không tồn tại: {file_path}")
    print("Tất cả file dữ liệu đã được tìm thấy.")

    # Đọc calendar và prices trước (nhỏ hơn, ít tốn bộ nhớ)
    print("Đang đọc file calendar.csv...")
    calendar = pd.read_csv(calendar_file)
    print("Đang đọc file sell_prices.csv...")
    prices = pd.read_csv(prices_file)

    # Đọc sales và lấy danh sách store_id duy nhất
    print("Đang đọc file sales_train_validation.csv để lấy danh sách store_id...")
    sales = pd.read_csv(sales_file, usecols=['store_id'])
    store_ids = sales['store_id'].unique()
    print(f"Danh sách cửa hàng: {store_ids}")

    # Tạo bảng rỗng trước để nhập dữ liệu theo từng phần
    print("Đang tạo bảng sales_raw...")
    pd.DataFrame(columns=['date', 'item_id', 'store_id', 'state_id', 'sales', 'sell_price']).to_sql(
        'sales_raw', engine, if_exists='replace', index=False, schema='public'
    )

    # Xử lý từng cửa hàng
    for store_id in store_ids:
        print(f"Đang xử lý cửa hàng: {store_id}...")
        
        # Đọc dữ liệu sales cho cửa hàng hiện tại
        print(f"Đang đọc dữ liệu sales cho {store_id}...")
        sales_chunk = pd.read_csv(sales_file)
        sales_chunk = sales_chunk[sales_chunk['store_id'] == store_id]

        # Unpivot dữ liệu sales
        print(f"Đang unpivot dữ liệu sales cho {store_id}...")
        sales_melted = pd.melt(
            sales_chunk,
            id_vars=['id', 'item_id', 'dept_id', 'cat_id', 'store_id', 'state_id'],
            var_name='d',
            value_name='sales'
        )

        # Ghép với calendar để lấy date
        print(f"Đang ghép với calendar để lấy date cho {store_id}...")
        sales_melted = sales_melted.merge(calendar[['d', 'date']], on='d', how='left')

        # Ghép với prices để lấy sell_price
        print(f"Đang ghép với sell_prices để lấy sell_price cho {store_id}...")
        prices_chunk = prices[prices['store_id'] == store_id]
        sales_melted = sales_melted.merge(
            prices_chunk.merge(calendar[['d', 'wm_yr_wk']], on='wm_yr_wk', how='left'),
            on=['store_id', 'item_id', 'd'],
            how='left'
        )

        # Lấy các cột cần thiết
        print(f"Đang chuẩn bị dữ liệu cuối cùng cho {store_id}...")
        sales_raw = sales_melted[['date', 'item_id', 'store_id', 'state_id', 'sales', 'sell_price']].copy()

        # Xử lý dữ liệu
        print(f"Đang xử lý dữ liệu (loại bỏ NaN và chuyển kiểu) cho {store_id}...")
        sales_raw['sales'] = pd.to_numeric(sales_raw['sales'], errors='coerce').fillna(0).astype(int)
        sales_raw['sell_price'] = pd.to_numeric(sales_raw['sell_price'], errors='coerce').fillna(0).astype(float)

        # Nhập vào PostgreSQL
        print(f"Đang nhập dữ liệu của {store_id} vào PostgreSQL...")
        sales_raw.to_sql('sales_raw', engine, if_exists='append', index=False, schema='public')
        print(f"Đã nhập dữ liệu cho {store_id} thành công!")

    print("Toàn bộ dữ liệu đã được nhập vào PostgreSQL thành công!")

except Exception as e:
    print(f"Lỗi: {e}")