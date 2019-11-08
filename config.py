import os

basedir =   os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI', '')
SQLALCHEMY_MIGRATE_REPO = os.getenv('DB_REPOSITORY', '')
SQLALCHEMY_TRACK_MODIFICATIONS = True

WTF_CSRF_ENABLED = True
SECRET_KEY = os.getenv('SECRET_KEY', '')

OAUTH_EMAIL_DOMAIN = os.getenv('OAUTH_EMAIL_DOMAIN', 'gmail.com')

class Auth:
    CLIENT_ID = os.getenv('CLIENT_ID', '')
    CLIENT_SECRET = os.getenv('CLIENT_SECRET', '')
    REDIRECT_URI = os.getenv('REDIRECT_URI', '')
    AUTH_URI = 'https://accounts.google.com/o/oauth2/auth'
    TOKEN_URI = 'https://accounts.google.com/o/oauth2/token'
    USER_INFO = 'https://www.googleapis.com/userinfo/v2/me'
    SCOPE = ['profile', 'email']