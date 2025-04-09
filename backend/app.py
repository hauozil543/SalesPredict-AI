from flask import Flask
from routes.chart import chart_bp  # Import Blueprint từ routes

app = Flask(__name__)

# Đăng ký Blueprint vào ứng dụng
app.register_blueprint(chart_bp, url_prefix='/chart')

if __name__ == '__main__':
    app.run(debug=True)
