# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config

# Initialize extensions, but don't attach them to an app yet
db = SQLAlchemy()
migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize Flask extensions with the app
    db.init_app(app)
    migrate.init_app(app, db)

    # Register Blueprints
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    # Import models here AFTER db is initialized and within app context
    # This is important for Flask-Migrate
    from app import models

    return app