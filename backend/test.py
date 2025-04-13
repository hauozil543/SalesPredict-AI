import sqlite3

conn = sqlite3.connect('m5_forecasting.db')
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(normalized_train_data);")
columns = cursor.fetchall()

for col in columns:
    print(col)

conn.close()
