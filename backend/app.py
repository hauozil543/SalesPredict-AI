from flask import Flask
from database.db_setup import init_db
from routes.home import home_bp
from routes.predict import predict_bp
from routes.history import history_bp

app = Flask(__name__)

# Khởi tạo database
init_db()

# Đăng ký blueprints
app.register_blueprint(home_bp)
app.register_blueprint(predict_bp)
app.register_blueprint(history_bp)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)