from markupsafe import Markup
from flask import Flask, redirect, request, g

from config import DB_URL, SECRET_KEY, JWT_AUTH_KEY
from db_setup import connect_db, db
from routes import auth_views, user_views,  customer_api, customer_views, order_api

import datetime
from deliveries.models import *

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['SECRET_KEY'] = SECRET_KEY


connect_db(app)
# db.drop_all()
# db.create_all()


#HTTPS ONLY
def https_redirect():
    if request.headers.get('X-Forwarded-Proto') == 'http':
        url = request.url.replace('http://', 'https://')
        return redirect(url)
    
#If a user_jwt is in the cookies, try to add that user to g
#otherwise, just move along
def add_user_to_g():
    #TODO double check that request.cookies is a dict of the cookies on the request
    if JWT_AUTH_KEY in request.cookies:
        try:
            user_jwt = request.cookies[JWT_AUTH_KEY]
            g.user = User.authenticate(user_jwt)
        except:
            g.user = None
    else:
        g.user = None

@app.before_request
def before_app_request():
    redirect = https_redirect()
    if redirect:
        return redirect
    add_user_to_g()

@app.template_filter('timeformat')
def format_date(value):
    format = "%I:%M%p"
    return datetime.date.strftime(value, format)

@app.template_filter('dateformat')
def format_date(value, format='medium'):
    if format == 'full':
        format = "%A, %B %d"
    elif format == 'medium':
        format = "%a, %b %d"
    return datetime.date.strftime(value, format)

app.register_blueprint(auth_views, url_prefix="")
app.register_blueprint(user_views, url_prefix="")
app.register_blueprint(customer_api, url_prefix="/api/customers")
app.register_blueprint(customer_views, url_prefix="/customers")

app.register_blueprint(order_api, url_prefix="/api/orders")


@app.route('/')
def show_homepage():
    return redirect('/current_delivery')
