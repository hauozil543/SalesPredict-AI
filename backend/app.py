from flask import Flask, jsonify
from database.db_setup import init_db
from routes.predict import predict_bp

app = Flask(__name__)

# Khởi tạo database
init_db()

# Đăng ký blueprints

app.register_blueprint(predict_bp, url_prefix='/api')

# Xử lý lỗi toàn cục
@app.errorhandler(Exception)
def handle_exception(e):
    return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)