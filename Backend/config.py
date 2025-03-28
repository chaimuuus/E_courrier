import os

API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
CLOUD_NAME = os.getenv("CLOUD_NAME")


class Config:
    # Define your configuration settings here
    SECRET_KEY = os.urandom(20)
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:chaima@localhost/ecourrier'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = 'localhost'
    MAIL_PORT = 1025
    MAIL_USE_SSL = False
    MAIL_USE_TLS = False
    MAIL_USERNAME = None
    MAIL_PASSWORD = None