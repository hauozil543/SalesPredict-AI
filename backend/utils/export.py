import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os

def export_to_csv(predictions):
    df = pd.DataFrame(predictions)
    filepath = 'static/history_export.csv'
    df.to_csv(filepath, index=False)
    return filepath

def export_to_pdf(predictions):
    filepath = 'static/history_export.pdf'
    c = canvas.Canvas(filepath, pagesize=letter)
    c.drawString(100, 750, "Prediction History Report")
    y = 700
    for pred in predictions:
        c.drawString(100, y, f"ID: {pred['id']}, Prediction: {pred['prediction']}, Date: {pred['prediction_date']}")
        y -= 20
        if y < 50:
            c.showPage()
            y = 750
    c.save()
    return filepath