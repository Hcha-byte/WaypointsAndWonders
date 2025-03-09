from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os

db = SQLAlchemy()

__version__ = '0.1.0'

def create_app():
    app = Flask(__name__)

    # Load configuration
    app.config.from_object('config.Config')

    # Initialize database
    db.init_app(app)
    migrate = Migrate(app, db)

    # Register Blueprints (for routes)
    from app.routes import main
    app.register_blueprint(main)

    return app
