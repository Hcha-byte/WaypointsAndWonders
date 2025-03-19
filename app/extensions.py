# app/extensions.py
from authlib.integrations.flask_client import OAuth
from flask_mail import Mail
import cloudinary.uploader
from run import app

mail = Mail()

# Initialize Cloudinary
cloudinary.config(
    cloud_name="dao2ekwrd",
    api_key="959777166196123",
    api_secret="CUooeSeQeIL5yFh7wyXlpJ20aJY"
)

# Initialize OAuth Google
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=app.config['GOOGLE_CLIENT_ID'],
    client_secret=app.config['GOOGLE_CLIENT_SECRET'],
    access_token_url='https://oauth2.googleapis.com/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    api_base_url='https://www.googleapis.com/oauth2/v2/',
    client_kwargs={'scope': 'openid email profile'},
)