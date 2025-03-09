import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'you_will_never_guess')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql://postgres:AWFPEJtYfLYfZsgbCcErKnORszcgCNRR@caboose.proxy.rlwy.net:12279/railway')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
