from flask import Flask, jsonify
from flask_cors import CORS
from routes.forecast import forecast_bp  # Import route dự báo

app = Flask(__name__)
CORS(app)  # Cho phép frontend React gọi API từ backend

# Đăng ký route
app.register_blueprint(forecast_bp, url_prefix='/api')

@app.route("/")
def home():
    return jsonify({"message": "Welcome to M5 Forecasting API"})

if __name__ == "__main__":
    app.run(debug=True)