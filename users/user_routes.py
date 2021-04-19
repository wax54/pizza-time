from flask import Blueprint, redirect, render_template, session, flash
from config import USER_KEY
from deliveries.models import Delivery
from users.models import User
import api.pag_api as api
user_views = Blueprint('user_routes', __name__)


def logged_in_user():
    if USER_KEY in session:
        u = User.get(session[USER_KEY])
        return u
    else:
        return False


@user_views.route('/current_delivery')
def show_current_delviery():
    u = logged_in_user()
    if not u:
        flash("Please Log In!")
        return redirect('/login')
    token = u.token
    email = u.email
    delivery = api.get_delivery(email=email, token=token)
    if delivery == False:
        #validation error
        return redirect('/login')
    if delivery['orders'] == []:
        #no delivery found
        flash("No Delivery Found!", "warning")
        return render_template('deliveries/current_delivery.html', delivery=delivery, name=u.name)
    if delivery['orders']:
        #successful credentials and delivery found
        Delivery.save_delivery(delivery=delivery, driver_id=u.id)
        return render_template('deliveries/current_delivery.html', delivery=delivery, name=u.name)
