import os

DB_URL = os.environ.get('DB_URL', 'postgresql:///pizza_time')
SECRET_KEY = os.environ.get('SECRET_KEY', "it's a secret")

USER_SESSION_KEY = 'CURR_USER'
API_SESSION_KEY = "CURR_API"
