import os

DB_URL = os.environ.get('DB_URL', 'postgresql:///pizza-time')
SECRET_KEY = os.environ.get('SECRET_KEY', "it's a secret")
