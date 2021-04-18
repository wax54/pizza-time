from config import DB_URL, SECRET_KEY
from db_setup import db, connect_db
from flask import Flask
from users.auth_routes import auth_views
from users.user_routes import user_views

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = SECRET_KEY


connect_db(app)
db.drop_all()
db.create_all()

app.register_blueprint(auth_views)
app.register_blueprint(user_views, url_prefix="/users")


@app.route('/')
def show_homepage():
    return """HELLO!"""
