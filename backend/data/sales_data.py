import pandas as pd

def load_sales_data():
    df = pd.read_csv('processed_data.csv')
    # Tổng hợp doanh số theo ngày
    sales_by_date = df.groupby('date')['sales'].sum().reset_index()
    # Tổng hợp giá bán trung bình theo ngày
    prices_by_date = df.groupby('date')['sell_price'].mean().reset_index()
    return sales_by_date, prices_by_date

def get_sales_data():
    sales_by_date, _ = load_sales_data()
    return {
        'dates': sales_by_date['date'].tolist(),
        'sales': sales_by_date['sales'].tolist()
    }

def get_prices_data():
    _, prices_by_date = load_sales_data()
    return {
        'dates': prices_by_date['date'].tolist(),
        'prices': prices_by_date['sell_price'].tolist()
    }