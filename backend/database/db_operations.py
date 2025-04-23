import sqlite3
import json

def insert_prediction(input_data, prediction):
    conn = sqlite3.connect('database/m5_forecasting.db')
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO predictions (input_data, prediction) VALUES (?, ?)',
        (json.dumps(input_data), float(prediction))
    )
    conn.commit()
    conn.close()

def get_all_predictions():
    conn = sqlite3.connect('database/m5_forecasting.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, input_data, prediction, prediction_date FROM predictions')
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            'id': row[0],
            'input_data': json.loads(row[1]),
            'prediction': row[2],
            'prediction_date': row[3]
        }
        for row in rows
    ]