from dotenv import load_dotenv

from app.security.summarizer.scheduler import init_scheduler
from .extensions import init_extensions

load_dotenv()
# Loads .env in current working directory by default
from flask import Flask
from flask_back import Back
from flask_login import LoginManager
from flask_migrate import Migrate
from .security.middleware import register_request_guards
from .security.honeypot import ensure_log_files

from app.models import User
from .admin.routes import admin
from .database import db

__version__ = '0.7.0'

from .search import ensure_index_with_retry

back = Back()


# noinspection PyTypeChecker
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
	app.config['MAIL_PASSWORD'] = app.config.get('MAIL_PASS', '')  # Use an App Password if using Gmail
	app.config['MAIL_DEFAULT_SENDER'] = 'contact@waypointsandwonders.com'
	
	app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
		"pool_pre_ping": True,  # Auto-detect & drop stale connections
		"pool_recycle":  1800,  # Recycle connections every 30 minutes
		"pool_size":     5,  # Keep only a few persistent connections
		"max_overflow":  2,  # Allow a couple of temporary overflow connections
		"pool_timeout":  15,  # Wait 15s for a connection from the pool
	}
	
	app.config['GOOGLE_CLIENT_ID'] = app.config.get('GOOGLE_CLIENT_ID', '')
	app.config['GOOGLE_CLIENT_SECRET'] = app.config.get('GOOGLE_CLIENT_SECRET', '')
	# </editor-fold>
	
	# <editor-fold desc="functions calls">
	init_extensions(app)
	register_request_guards(app)
	ensure_log_files()
	from app.cli import register_commands
	register_commands(app)
	init_scheduler(app)
	# </editor-fold>
	
	# <editor-fold desc="db-config">
	# Initialize database
	db.init_app(app)
	migrate = Migrate(app, db)
	# </editor-fold>
	
	# <editor-fold desc="extensions init">
	# Initialize login
	login_manager = LoginManager()
	login_manager.init_app(app)
	
	back.init_app(app, excluded_endpoints=['admin', 'auth'], default_url='/index', use_referrer=True,
	              home_urls=['/index', '/', '/search'])
	# Register user loader
	login_manager.user_loader(User.user_loder)
	login_manager.login_view = "auth.login"
	# </editor-fold>
	
	# <editor-fold desc="blueprints init">
	# Import each blueprint
	from app.main import main_bp
	from app.posts import posts_bp
	from app.admin import admin_bp
	from app.auth import auth_bp
	from app.search import search_bp
	from app.security.honeypot import honeypot_bp
	from app.security.log_viewer import log_viewer_bp
	
	# Register Blueprints (for routes)
	app.register_blueprint(main_bp)
	app.register_blueprint(search_bp, url_prefix='/search')
	app.register_blueprint(posts_bp, url_prefix='/post')  # posts at /post/<id>
	app.register_blueprint(admin_bp, url_prefix='/admin')
	app.register_blueprint(auth_bp, url_prefix='/auth')
	app.register_blueprint(honeypot_bp)
	app.register_blueprint(log_viewer_bp, url_prefix='/log')
	
	import logging
	import sys
	from app.logging.log_colorizer import ColorFormatter
	
	handler = logging.StreamHandler(sys.stdout)
	formatter = ColorFormatter(
		"[%(asctime)s] [%(levelname)s] %(message)s",
		datefmt="%Y-%m-%d %H:%M:%S %Z"
	)
	handler.setFormatter(formatter)
	log_level = app.config["LOG_LEVEL"]
	# Don't clear handlers—root logger already has what it needs
	logging.getLogger("flask.app").setLevel(log_level)
	logging.getLogger("app").setLevel(log_level)
	logging.getLogger("werkzeug").setLevel(log_level)
	logging.getLogger("urllib3").setLevel(log_level)
	logging.getLogger("requests").setLevel(log_level)
	
	ensure_index_with_retry(app=app)
	from app.visitor_logging import register_single_visit_logger
	register_single_visit_logger(app)
	app.logger.debug("🚀 Server started")
	return app
# </editor-fold>
