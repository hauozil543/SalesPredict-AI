import sqlite3
import pandas as pd

conn = sqlite3.connect('historical_data.db')
query = "SELECT date, sales, sell_price, day_of_week, snap_CA, is_holiday FROM historical_data WHERE item_id = 'FOODS_1_218' AND store_id = 'CA_1' AND date <= '2016-04-24' ORDER BY date DESC LIMIT 28"
df = pd.read_sql_query(query, conn)
conn.close()
print(df)