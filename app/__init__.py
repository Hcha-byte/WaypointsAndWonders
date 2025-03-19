from flask import Flask
from flask_login import LoginManager
from .database import db
from flask_migrate import Migrate
from app.models import User



__version__ = '0.1.0'

def create_app():
    app = Flask(__name__)

    # Load configuration
    app.config.from_object('config.Config')
    
    # Configure Flask-Mail with your email provider
    # TODO configur for WPAW email
    app.config['MAIL_SERVER'] = 'mail.privateemail.com'  # Change for your provider
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_USE_SSL'] = True
    app.config['MAIL_DEBUG'] = True
    app.config['MAIL_USERNAME'] = 'contact@waypointsandwonders.com'  # Replace with your email
    app.config['MAIL_PASSWORD'] = 'ropfy6-sapmyq-bujJer'  # Use an App Password if using Gmail
    app.config['MAIL_DEFAULT_SENDER'] = 'contact@waypointsandwonders.com'
    app.config['GOOGLE_CLIENT_ID'] = '735507344079-1u1080giul9513s8sdhub5dam9vuuu4d.apps.googleusercontent.com'
    app.config['GOOGLE_CLIENT_SECRET'] = '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'
    

    
    # Initialize database
    db.init_app(app)
    migrate = Migrate(app, db)
    
    # Initialize login
    login_manager = LoginManager()
    login_manager.init_app(app)
    
    # Register user loader
    login_manager.user_loader(User.user_loder)
    login_manager.login_view = "main.login"
    

    # Import and initialize extensions
    from .extensions import mail, oauth
    mail.init_app(app)
    oauth.init_app(app)

    # Register Blueprints (for routes)
    from app.routes import main
    app.register_blueprint(main)

    return app
