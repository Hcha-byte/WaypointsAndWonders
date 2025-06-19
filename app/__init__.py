from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate

from app.models import User
from .database import db

__version__ = '0.6.0'


def create_app():
	app = Flask(__name__)
	
	# Load configuration
	app.config.from_object('config.Config')
	
	# <editor-fold desc="Flask-config">
	# Configure Flask-Mail with your email provider
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
	# </editor-fold>
	
	# <editor-fold desc="db-config">
	# Initialize database
	db.init_app(app)
	migrate = Migrate(app, db)
	# </editor-fold>
	
	# <editor-fold desc="login-config">
	# Initialize login
	login_manager = LoginManager()
	login_manager.init_app(app)
	
	# Register user loader
	login_manager.user_loader(User.user_loder)
	login_manager.login_view = "main.login"
	# </editor-fold>
	
	# <editor-fold desc="misc-config">
	# Import and initialize extensions
	from .extensions import mail, oauth
	mail.init_app(app)
	oauth.init_app(app)
	
	# Import each blueprint
	from app.main import main_bp
	from app.posts import posts_bp
	from app.admin import admin_bp
	from app.auth import auth_bp
	from app.search import search_bp
	
	# Register Blueprints (for routes)
	app.register_blueprint(main_bp)
	app.register_blueprint(search_bp, url_prefix='/search')
	app.register_blueprint(posts_bp, url_prefix='/post')  # posts at /post/<id>
	app.register_blueprint(admin_bp, url_prefix='/admin')
	app.register_blueprint(auth_bp, url_prefix='/auth')
	
	return app
# </editor-fold>
