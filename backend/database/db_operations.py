import pandas as pd
import sqlite3

def get_historical_data(item_idx, store_idx):
    """
    Lấy dữ liệu lịch sử từ processed_data.db dựa trên item_idx và store_idx.
    """
    conn = sqlite3.connect('processed_data.db')
    query = """
    SELECT *
    FROM data
    WHERE item_idx = ? AND store_idx = ?
    ORDER BY date
    """
    df = pd.read_sql_query(query, conn, params=(item_idx, store_idx))
    conn.close()
    return df