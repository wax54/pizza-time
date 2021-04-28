from flask import Blueprint, redirect, render_template, session, g
from config import USER_SESSION_KEY, API_SESSION_KEY
from customers.models import Customer
from users.models import User

customer_views = Blueprint('customer_views', __name__)


@customer_views.before_request
def add_user_to_g_or_redirect():
    """If we're logged in, add curr user to Flask global.
    otherwise, redirect them to login"""
    if USER_SESSION_KEY in session:
        g.user = User.query.get(session[USER_SESSION_KEY])
        if not g.user:
            flash("Please Log In!")
            return redirect('/login')
    else:
        flash("Please Log In!")
        return redirect('/login')


@customer_views.route('/<id>')
def view_customer(id):
    customer = Customer.query.get(id)

    return render_template("customers/view_one.html", customer=customer)
