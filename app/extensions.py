# app/extensions.py
import os

import cloudinary.uploader
import meilisearch
import redis
from authlib.integrations.flask_client import OAuth
from flask_mail import Mail
from rq import Queue

mail = Mail()

# Initialize Cloudinary
cloudinary.config(
	cloud_name="dao2ekwrd",
	api_key="959777166196123",
	api_secret="CUooeSeQeIL5yFh7wyXlpJ20aJY"
)

# Initialize OAuth Google
oauth = OAuth()
google = oauth.register(
	name='google',
	client_id='735507344079-1u1080giul9513s8sdhub5dam9vuuu4d.apps.googleusercontent.com',
	client_secret='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',
	access_token_url='https://oauth2.googleapis.com/token',
	authorize_url='https://accounts.google.com/o/oauth2/auth',
	api_base_url='https://www.googleapis.com/oauth2/v2/',
	client_kwargs={'scope': 'openid email profile'},
	server_metadata_url="https://accounts.google.com/.well-known/openid-configuration"
)

client = meilisearch.Client(
	os.environ["MEILI_URL"],
	os.environ["MEILI_API_KEY"]
)

# Connect to Redis
redis_conn = redis.from_url(os.getenv("REDIS_URL"))
q = Queue(connection=redis_conn)
