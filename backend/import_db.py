import pandas as pd
from sqlalchemy import create_engine, text
import os
from sqlalchemy.exc import SQLAlchemyError

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

    # Xóa các bảng theo thứ tự (bảng phụ thuộc trước, bảng cha sau)
    print("Đang xóa các bảng cũ (nếu tồn tại)...")
    with engine.connect() as connection:
        connection.execute(text("DROP TABLE IF EXISTS sales CASCADE;"))
        connection.execute(text("DROP TABLE IF EXISTS prices CASCADE;"))
        connection.execute(text("DROP TABLE IF EXISTS calendar CASCADE;"))
        connection.commit()
    print("Đã xóa các bảng cũ thành công!")

    # Tạo bảng calendar
    print("Đang tạo bảng calendar...")
    create_calendar_table_query = """
    CREATE TABLE IF NOT EXISTS calendar (
        d_id VARCHAR(10) PRIMARY KEY,
        date DATE,
        wm_yr_wk INT
    );
    """
    with engine.connect() as connection:
        connection.execute(text(create_calendar_table_query))
        connection.commit()
    print("Bảng calendar đã được tạo thành công!")

    # Tạo bảng prices
    print("Đang tạo bảng prices...")
    create_prices_table_query = """
    CREATE TABLE IF NOT EXISTS prices (
        price_id SERIAL PRIMARY KEY,
        item_id VARCHAR(20),
        store_id VARCHAR(10),
        wm_yr_wk INT,
        sell_price FLOAT
    );
    """
    with engine.connect() as connection:
        connection.execute(text(create_prices_table_query))
        connection.commit()
    print("Bảng prices đã được tạo thành công!")

    # Tạo bảng sales
    print("Đang tạo bảng sales...")
    create_sales_table_query = """
    CREATE TABLE IF NOT EXISTS sales (
        sale_id SERIAL PRIMARY KEY,
        item_id VARCHAR(20),
        dept_id VARCHAR(20),
        cat_id VARCHAR(20),
        store_id VARCHAR(10),
        state_id VARCHAR(10),
        d_id VARCHAR(10),
        sales INTEGER,
        FOREIGN KEY (d_id) REFERENCES calendar(d_id)
    );
    """
    with engine.connect() as connection:
        connection.execute(text(create_sales_table_query))
        connection.commit()
    print("Bảng sales đã được tạo thành công!")

    # Đọc calendar và lọc theo khoảng thời gian (d_702 đến d_1913)
    print("Đang đọc và lọc file calendar.csv...")
    calendar = pd.read_csv(calendar_file)
    calendar['date'] = pd.to_datetime(calendar['date'])
    start_date = '2013-01-01'  # d_702
    end_d = 'd_1913'           # 2016-04-24
    end_date = calendar[calendar['d'] == end_d]['date'].iloc[0]
    calendar = calendar[(calendar['date'] >= start_date) & (calendar['d'] <= end_d)]
    calendar = calendar.rename(columns={'d': 'd_id'})  # Đổi tên cột d thành d_id
    print(f"Kích thước calendar sau khi lọc: {calendar.shape}")

    # Nhập dữ liệu vào bảng calendar
    print("Đang nhập dữ liệu vào bảng calendar...")
    # Sử dụng if_exists='append' vì bảng đã được tạo và xóa dữ liệu trước đó
    calendar[['d_id', 'date', 'wm_yr_wk']].to_sql('calendar', engine, if_exists='append', index=False, schema='public')
    print("Đã nhập dữ liệu vào bảng calendar thành công!")

    # Đọc prices
    print("Đang đọc file sell_prices.csv...")
    prices = pd.read_csv(prices_file)
    print(f"Kích thước sell_prices: {prices.shape}")

    # Nhập dữ liệu vào bảng prices
    print("Đang nhập dữ liệu vào bảng prices...")
    prices[['item_id', 'store_id', 'wm_yr_wk', 'sell_price']].to_sql('prices', engine, if_exists='append', index=False, schema='public')
    print("Đã nhập dữ liệu vào bảng prices thành công!")

    # Đọc sales và lấy danh sách store_id duy nhất
    print("Đang đọc file sales_train_validation.csv để lấy danh sách store_id...")
    sales = pd.read_csv(sales_file, usecols=['store_id'])
    store_ids = sales['store_id'].unique()
    print(f"Danh sách cửa hàng: {store_ids}")

    # Lấy danh sách các giá trị d hợp lệ từ calendar
    valid_d_values = calendar['d_id'].tolist()
    print(f"Số lượng giá trị d hợp lệ: {len(valid_d_values)} (từ {valid_d_values[0]} đến {valid_d_values[-1]})")

    # Xử lý từng cửa hàng
    for store_id in store_ids:
        print(f"Đang xử lý cửa hàng: {store_id}...")
        
        # Đọc dữ liệu sales cho cửa hàng hiện tại
        print(f"Đang đọc dữ liệu sales cho {store_id}...")
        d_columns = ['id', 'item_id', 'dept_id', 'cat_id', 'store_id', 'state_id'] + valid_d_values
        sales_chunk = pd.read_csv(sales_file, usecols=d_columns)
        sales_chunk = sales_chunk[sales_chunk['store_id'] == store_id]
        print(f"Kích thước sales_chunk cho {store_id}: {sales_chunk.shape}")

        # Unpivot dữ liệu sales
        print(f"Đang unpivot dữ liệu sales cho {store_id}...")
        sales_melted = pd.melt(
            sales_chunk,
            id_vars=['id', 'item_id', 'dept_id', 'cat_id', 'store_id', 'state_id'],
            var_name='d_id',
            value_name='sales'
        )

        # Lọc sales_melted để chỉ lấy các giá trị d hợp lệ (d_702 đến d_1913)
        print(f"Đang lọc sales_melted để chỉ lấy các giá trị d hợp lệ cho {store_id}...")
        sales_melted = sales_melted[sales_melted['d_id'].isin(valid_d_values)]
        print(f"Kích thước sales_melted sau khi lọc: {sales_melted.shape}")

        # Xử lý dữ liệu
        print(f"Đang xử lý dữ liệu (chuyển kiểu) cho {store_id}...")
        sales_melted['sales'] = pd.to_numeric(sales_melted['sales'], errors='coerce').fillna(0).astype(int)

        # Nhập dữ liệu vào bảng sales
        print(f"Đang nhập dữ liệu của {store_id} vào bảng sales...")
        sales_melted[['item_id', 'dept_id', 'cat_id', 'store_id', 'state_id', 'd_id', 'sales']].to_sql('sales', engine, if_exists='append', index=False, schema='public')
        print(f"Đã nhập dữ liệu cho {store_id} vào bảng sales thành công!")

    print("Toàn bộ dữ liệu (2013-01-01 đến 2016-04-24, d_702 đến d_1913) đã được nhập vào PostgreSQL thành công!")

except SQLAlchemyError as e:
    print(f"Lỗi SQLAlchemy: {e}")
except Exception as e:
    print(f"Lỗi khác: {e}")