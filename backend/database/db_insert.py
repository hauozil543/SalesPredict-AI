import sqlite3
import pandas as pd

# Kết nối database
conn = sqlite3.connect("m5_forecasting.db")

# Nhập dữ liệu từ calendar.csv

df_calendar = pd.read_csv("../../data/raw/calendar.csv")

df_calendar.to_sql("calendar", conn, if_exists="replace", index=False)  # Ghi vào SQLite

conn.close()
print("✅ Dữ liệu đã được nhập vào SQLite!")
