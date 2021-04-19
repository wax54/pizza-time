from flask import Blueprint, render_template, session, redirect, flash
from config import USER_KEY
from users.forms import PagUserLogin
from users.models import User
import pag_api as api

auth_views = Blueprint('auth_routes', __name__)


@auth_views.route('/login', methods=["GET", "POST"])
def login():
    form = PagUserLogin()
    if form.validate_on_submit():
        email = form.email.data
        password = form.passord.data
        token = api.login(email=email, password=password)
        if token:
            #successful credentials
            u_id = User.create_or_update(email=email, token=token)
            session[USER_KEY] = u_id
            return redirect('/pag/current_delivery')
        else:
            flash("Not Valid Credentials!", "danger")
    return render_template('user_login.html', form=form)
