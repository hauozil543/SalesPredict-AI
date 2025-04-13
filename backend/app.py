from flask import Flask
from routes.forecast import forecast_bp
from routes.sales_history import sales_history_bp
from routes.items import items_bp
from routes.metric import metrics_bp
from routes.calendar1 import calendar_bp

app = Flask(__name__)

# Đăng ký blueprint
app.register_blueprint(forecast_bp)
app.register_blueprint(sales_history_bp)
app.register_blueprint(items_bp)
app.register_blueprint(metrics_bp)
app.register_blueprint(calendar_bp)

if __name__ == '__main__':
    app.run(debug=True)
