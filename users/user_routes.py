from flask import Blueprint, redirect, render_template
from config import USER_KEY

user_views = Blueprint('user_routes', __name__)


def user_logged_in():
    if USER_KEY in session:
        u = User.get(session[USER_KEY])
        return u
    else:
        return False


@user_views.route('/current_delivery')
def show_current_delviery():
    u = logged_in_user()
    if not u:
        return redirect('/login')
    token = u.token
    email = u.email
    delivery = api.get_delivery(email=email, token=token)
    if delivery == False:
        #validation error
        return redirect('/login')
    if delivery == []:
        #no delivery found
        flash("No Delivery Found!", "info")
        return render_template('current_delivery.html', delivery=delivery, name=u.name)
    if delivery:
        #successful credentials and delivery found
        u_id = User.create_or_update(email=email, token=token)
        return render_template('current_delivery.html', delivery=delivery, name=u.name)
