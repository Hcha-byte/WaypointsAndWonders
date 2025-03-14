import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'you_will_never_guess')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql://postgres:mpBThkxtbtVJnhvfRGIrxJNhdLmVVRUS@switchyard.proxy.rlwy.net:23186/railway')
