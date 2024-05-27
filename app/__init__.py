from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from config import Config

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    Bootstrap(app)

    with app.app_context():
        from .views.main_views import main_bp
        from .views.data_views import data_bp, charts_bp

        app.register_blueprint(main_bp)
        app.register_blueprint(data_bp)
        app.register_blueprint(charts_bp)
        db.create_all()  # Create tables if they don't exist

    return app
