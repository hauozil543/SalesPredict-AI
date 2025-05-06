from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class HistoryData(db.Model):
    __tablename__ = 'history_data'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    dept = db.Column(db.String(50), nullable=False)
    item_id = db.Column(db.String(50), nullable=False)
    date = db.Column(db.Date, nullable=False)
    predicted_sales = db.Column(db.Float, nullable=False)