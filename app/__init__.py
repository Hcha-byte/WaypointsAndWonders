from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from .database import db
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
from werkzeug.middleware.proxy_fix import ProxyFix
from app.models import User



__version__ = '0.1.0'

def create_app():
    app = Flask(__name__)

    # Load configuration
    app.config.from_object('config.Config')
    app.config["SESSION_COOKIE_SECURE"] = False  # Disable secure cookies for testing
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

    # Initialize database
    db.init_app(app)
    migrate = Migrate(app, db)

    login_manager = LoginManager()
    login_manager.init_app(app)
    
    login_manager.user_loader(User.user_loder)
    login_manager.login_view = "main.login"
    
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_host=1)

    # Register Blueprints (for routes)
    from app.routes import main
    app.register_blueprint(main)

    return app
