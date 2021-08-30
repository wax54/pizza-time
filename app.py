from markupsafe import Markup
from flask import Flask, redirect, request, g
from helpers.middleware import add_user_to_g, https_redirect
from config import DB_URL, SECRET_KEY, JWT_AUTH_KEY
from db_setup import connect_db, db
from routes import auth_views, user_views,  customer_api, customer_views, order_api
import urllib

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


@app.before_request
def before_app_request():
    #redrect to https
    redirect = https_redirect()
    if redirect:
        return redirect
    #add user info to global var
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


def urlencode(string):
    """encode a string to be added to a url"""
    return urllib.parse.quote_plus(string)

#TODO
#Finish up this func
@app.template_filter('get_nav_all_link')
def get_nav_all_link(delivery):
    """returns a google maps link with all the addresses naved in order"""
    #https://www.google.com/maps/dir/?api=1&origin=Paris%2CFrance&destination=Cherbourg%2CFrance&travelmode=driving&waypoints=Versailles%2CFrance%7CChartres%2CFrance%7CLe+Mans%2CFrance%7CCaen%2CFrance
    store = delivery['store']
    #TODO get store address
    #   set store address as destination
    #   get rid of addresses.pop
    orders = delivery['orders']
    addresses = [urlencode(o['address']) for o in orders]
    dest = addresses.pop()
    waypoints = "%7C".join(addresses)
    link = "https://www.google.com/maps/dir/?api=1&destination="+dest
    if waypoints:
        link += "&waypoints="+waypoints
    return link


app.register_blueprint(auth_views, url_prefix="")
app.register_blueprint(user_views, url_prefix="")
app.register_blueprint(customer_api, url_prefix="/api/customers")
app.register_blueprint(customer_views, url_prefix="/customers")

app.register_blueprint(order_api, url_prefix="/api/orders")


@app.route('/')
def show_homepage():
    return redirect('/current_delivery')
