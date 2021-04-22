from flask import Blueprint, render_template, session, redirect, flash
from config import USER_KEY
from users.forms import PagUserLogin
from users.models import User
import api.pag_api as api

auth_views = Blueprint('auth_routes', __name__)


@auth_views.route('/login', methods=["GET", "POST"])
def login():
    """Displays the login form on GET 
    Attempts to Log the user into the API on POST"""
    #get the form
    form = PagUserLogin()
    #see if its a POST and if all required data is there
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        #attempt to login to the API
        token = api.login(email=email, password=password)
        #if success
        if token:
            #save them in the DB
            u_id = User.create_or_update(email=email, token=token)
            #put the id in the session
            session[USER_KEY] = u_id
            #redirect to curr_del page
            return redirect('/pag/current_delivery')
        else:
            #login failed
            flash("Not Valid Credentials!", "danger")
            #return to login page
            return render_template('user_login.html', form=form)
    else:
        #show login page
        return render_template('user_login.html', form=form)
