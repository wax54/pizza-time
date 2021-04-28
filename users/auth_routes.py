from flask import Blueprint, render_template, session, redirect, flash
from config import USER_SESSION_KEY, API_SESSION_KEY
from users.forms import UserLogin
from users.models import User
from api import apis

auth_views = Blueprint('auth_routes', __name__)


@auth_views.route('/login', methods=["GET", "POST"])
def login_to_pag():
    """Displays the login form on GET 
    Attempts to Log the user into the API on POST"""
    #get the form
    form = UserLogin()
    #see if its a POST and if all required data is there
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        api_key = form.api.data
        #set the API to use
        api = apis[api_key]
        #attempt to login to the API
        token = api.login(email=email, password=password)
        #if success
        if token:
            #save them in the DB
            u_id = User.create_or_update(email=email, token=token)
            #put the id in the session
            session[USER_SESSION_KEY] = u_id
            session[API_SESSION_KEY] = api_key

            #redirect to curr_del page
            return redirect('/current_delivery')
        else:
            #login failed
            flash("Not Valid Credentials!", "danger")
            #return to login page
            return render_template('user_login.html', form=form)
    else:
        #show login page
        return render_template('user_login.html', form=form)
