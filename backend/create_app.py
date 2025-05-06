from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from backend.routes.predict import bp as predict_bp
from backend.routes.history import bp as history_bp
from backend.routes.home import bp as home_bp

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:H30012003h@localhost:5432/m5_data_processed'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    app.register_blueprint(predict_bp)
    app.register_blueprint(history_bp)
    app.register_blueprint(home_bp)
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)