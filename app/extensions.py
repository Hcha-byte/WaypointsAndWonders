# app/extensions.py
import os

import cloudinary.uploader
import typesense
from authlib.integrations.flask_client import OAuth
from flask_mail import Mail

mail = Mail()

# Initialize Cloudinary
cloudinary.config(
	cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME', ''),
	api_key=os.getenv('CLOUDINARY_API_KEY', ''),
	api_secret=os.getenv('CLOUDINARY_API_SECRET', ''),
)

# Initialize OAuth Google
oauth = OAuth()
google = oauth.register(
	name='google',
	client_id=os.getenv('GOOGLE_CLIENT_ID', ''),
	client_secret=os.getenv('GOOGLE_CLIENT_SECRET', ''),
	access_token_url='https://oauth2.googleapis.com/token',
	authorize_url='https://accounts.google.com/o/oauth2/auth',
	api_base_url='https://www.googleapis.com/oauth2/v2/',
	client_kwargs={'scope': 'openid email profile'},
	server_metadata_url="https://accounts.google.com/.well-known/openid-configuration"
)

# noinspection PyTypeChecker
client = typesense.Client({
	'api_key': os.getenv('TYPESENSE_API_KEY', ''),  # must match Dockerfile
	'nodes': [{
		'host': 'typesense-main.up.railway.app',  # no https
		'port': 443,
		'protocol': 'https'
	}],
	'connection_timeout_seconds': 2
})
