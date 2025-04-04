import sqlite3

conn = sqlite3.connect("m5_forecasting.db")
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS calendar (
        date TEXT PRIMARY KEY,
        wm_yr_wk INTEGER,
        weekday TEXT,
        month INTEGER,
        year INTEGER,
        event_name_1 TEXT,
        event_type_1 TEXT,
        event_name_2 TEXT,
        event_type_2 TEXT,
        snap_CA INTEGER,
        snap_TX INTEGER,
        snap_WI INTEGER
    )
''')

conn.commit()
conn.close()
print("✅ Database và bảng calendar đã được tạo!")
