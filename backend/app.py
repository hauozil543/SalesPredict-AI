from flask import Flask
from routes.predict import predict_bp
from routes.home import home_bp
import os
from flask_cors import CORS
print("Thư mục làm việc hiện tại:", os.getcwd())
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})  # Cho phép frontend truy cập
# Đăng ký blueprint từ routes/predict.py
app.register_blueprint(predict_bp)
app.register_blueprint(home_bp)
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)