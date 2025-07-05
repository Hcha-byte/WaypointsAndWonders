# app/extensions.py
import cloudinary.uploader
import typesense
from authlib.integrations.flask_client import OAuth
from flask import Flask
from flask_mail import Mail
from itsdangerous import URLSafeTimedSerializer

mail = None
oauth = None
google = None
client = None
serializer = None


def init_extensions(app: Flask):
	global mail
	global oauth
	global google
	global client
	global serializer
	# Initialize Flask-Mail
	mail = Mail()
	mail.init_app(app)
	# Initialize Cloudinary
	cloudinary.config(
		cloud_name=app.config.get('CLOUDINARY_CLOUD_NAME', ''),
		api_key=app.config.get('CLOUDINARY_API_KEY', ''),
		api_secret=app.config.get('CLOUDINARY_API_SECRET', ''),
	)
	serializer = URLSafeTimedSerializer(app.config.get("SECRET_KEY", "you_will_never_guess"))
	# Initialize OAuth Google
	oauth = OAuth()
	
	google = oauth.register(
		name='google',
		client_id=app.config.get('GOOGLE_CLIENT_ID', ''),
		client_secret=app.config.get('GOOGLE_CLIENT_SECRET', ''),
		access_token_url='https://oauth2.googleapis.com/token',
		authorize_url='https://accounts.google.com/o/oauth2/auth',
		api_base_url='https://www.googleapis.com/oauth2/v2/',
		client_kwargs={'scope': 'openid email profile'},
		server_metadata_url="https://accounts.google.com/.well-known/openid-configuration"
	)
	oauth.init_app(app)
	
	# noinspection PyTypeChecker
	client = typesense.Client({
		'api_key':                    app.config.get('TYPESENSE_API_KEY', ''),  # must match Dockerfile
		'nodes':                      [{
			'host':     'typesense-main.up.railway.app',  # no https
			'port':     443,
			'protocol': 'https'
		}],
		'connection_timeout_seconds': 2
	})


def get_typesense_client():
	global client
	if client is None:
		raise RuntimeError("Typesense client not initialized!")
	return client
