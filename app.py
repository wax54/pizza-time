from markupsafe import Markup
from flask import Flask, redirect

from config import DB_URL, SECRET_KEY
from db_setup import connect_db, db
from users.__init__ import auth_views, user_views
import datetime
from deliveries.models import *

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = SECRET_KEY


connect_db(app)
# db.drop_all()
# db.create_all()


@app.template_filter('dateformat')
def format_date(value, format='medium'):
    if format == 'full':
        format = "%A, %B %d"
    elif format == 'medium':
        format = "%a, %b %d"
    return datetime.date.strftime(value, format)

app.register_blueprint(auth_views, url_prefix="")
app.register_blueprint(user_views, url_prefix="")


@app.route('/')
def show_homepage():
    return redirect('/login')
