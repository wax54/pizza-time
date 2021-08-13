import os
import datetime

DB_URL = os.environ.get('DB_URL', 'postgresql:///pizza_time')
SECRET_KEY = os.environ.get('SECRET_KEY', "it's a secret")

RENEWAL_TIMEFRAME = datetime.timedelta(days=3)


USER_SESSION_KEY = 'CURR_USER'
ACCESSOR_SESSION_KEY = 'CURR_USER_ACCESSOR'
API_SESSION_KEY = "CURR_API"
JWT_AUTH_KEY = "PIZZA_AUTH"
