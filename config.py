import os


class Config:
	SECRET_KEY = os.environ.get('SECRET_KEY', 'you_will_never_guess')
	SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', '')
	
	TYPESENSE_API_KEY = os.environ.get("TYPESENSE_API_KEY", "")
	TYPESENSE_HOST = os.environ.get("TYPESENSE_HOST", "")
	MAIL_PASS = os.environ.get("MAIL_PASS", "")
	GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")
	GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "")
	CLOUDINARY_CLOUD_NAME = os.environ.get("CLOUDINARY_CLOUD_NAME", "")
	CLOUDINARY_API_KEY = os.environ.get("CLOUDINARY_API_KEY", "")
	CLOUDINARY_API_SECRET = os.environ.get("CLOUDINARY_API_SECRET", "")
