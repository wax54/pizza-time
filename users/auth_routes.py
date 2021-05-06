from flask import Blueprint, render_template, session, redirect, flash
from config import USER_SESSION_KEY, API_SESSION_KEY
from users.forms import UserLogin, DemoUserLogin, PagUserLogin
from users.models import User
from api import apis, PAG_KEY, DEMO_KEY

auth_views = Blueprint('auth_routes', __name__)


@auth_views.route('/logout', methods=["GET", "POST"])
def logout_user():
    session[USER_SESSION_KEY] = None
    session[API_SESSION_KEY] = None
    return redirect('/login')
    
@auth_views.route('/login')
def choose_login():
    api_key = session.get(API_SESSION_KEY)
    print("****************", api_key)
    if api_key:
        if api_key == DEMO_KEY:
            return redirect('/demo/login')
        if api_key == PAG_KEY:
            return redirect('/pag/login')
    else:
        return render_template("choose_login.html")

@auth_views.route('/demo/login', methods=["GET", "POST"])
def login_to_demo():
    """Displays the login form on GET 
    Attempts to Log the user into the DEMO API on POST"""
    #get the form
    form = DemoUserLogin()
    #see if its a POST and if all required data is there
    if form.validate_on_submit():
        name = form.name.data
        api_key = DEMO_KEY

        #set the API to use the Pag api
        api = apis[api_key]
        #delete the old user, along with their notes and orders
        #User.delete_by_email(email="demo_user2")
        #make a new user
        token = api.login()
        try:
            u_id = User.create(name=name, email="demo_user2", token=token, api_id=api_key)
            #put the id in the session
            session[USER_SESSION_KEY] = u_id
            session[API_SESSION_KEY] = DEMO_KEY
            #redirect to curr_del page
            return redirect('/current_delivery')
        except:
            #login failed
            flash("Woah there Buddy, Try That Again.", "danger")
            #return to login page
            return render_template('user_login.html', form=form)
    else:
        #show login page
        return render_template('user_login.html', form=form)

@auth_views.route('/pag/login', methods=["GET", "POST"])
def login_to_pag():
    """Displays the login form on GET 
    Attempts to Log the user into the PAG API on POST"""
    #get the form
    form = PagUserLogin()
    #see if its a POST and if all required data is there
    if form.validate_on_submit():

        name = form.name.data
        email = form.email.data
        password = form.password.data
        
        api_key = PAG_KEY
        
        #set the API to use the Pag api
        api = apis[api_key]
        #attempt to login to the API
        token = api.login(email=email, password=password)
        #if success
        if token:
            #save them in the DB
            u_id = User.create_or_update(
                name=name, email=email, token=token, api_id=api_key)
            
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


@auth_views.route('/multi/login', methods=["GET", "POST"])
def login_multi():
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
            u_id = User.create_or_update(email=email, token=token, api_id=api_key)
            #put the id in the session
            session[USER_SESSION_KEY] = u_id

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
