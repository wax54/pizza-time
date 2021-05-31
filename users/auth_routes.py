from flask import Blueprint, render_template, session, redirect, flash, make_response
from config import USER_SESSION_KEY, API_SESSION_KEY, USER_ACCESSOR_KEY, JWT_AUTH_KEY, SECRET_KEY
from users.forms import UserLogin, DemoUserLogin, PagUserLogin
from users.models import User
from api import apis, PAG_KEY, DEMO_KEY
import jwt

auth_views = Blueprint('auth_routes', __name__)


@auth_views.route('/logout', methods=["GET", "POST"])
def logout_user():
    session[USER_SESSION_KEY] = None
    session[API_SESSION_KEY] = None
    return redirect('/login')
    
@auth_views.route('/login')
def choose_login():
    api_key = session.get(API_SESSION_KEY)
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
        token_glob = api.login()
        token = token_glob['token']
        expiration = token_glob['expiration']
        try:
            u = User.create(name=name, 
                            email="demo_user2", 
                            token=token, 
                            token_expiration=expiration, 
                            api_id=api_key)
            
            #This will be false if the user was never created
            hashed_accessor = User.update_accessor(u.id)
            
            #JWT payload looks like {USER_ACCESSOR_KEY: hashed_accessor, USER_SESSION_KEY: u.id}
            user_jwt = jwt.encode({ 
                                USER_ACCESSOR_KEY: hashed_accessor, 
                                USER_SESSION_KEY: u.id 
                                }, 
                                SECRET_KEY,
                                algorithm="HS256")
            #put the id and api in the session
            session[USER_SESSION_KEY] = u.id
            session[API_SESSION_KEY] = DEMO_KEY
            
            #TODO change pag and multi login
            
            #redirect to curr_del page
            resp = make_response(redirect('/current_delivery'))
            #put the auth and api in the cookies
            resp.set_cookie(JWT_AUTH_KEY, user_jwt, 
                            expires=u.accessor_expiration)
            resp.set_cookie(API_SESSION_KEY, DEMO_KEY,
                            expires=u.accessor_expiration)
            
            return resp 
        except Exception as e:
            #login failed
            flash("Woah there Buddy, Try That Again.", "danger")
            print(e)
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
        token_glob = api.login(email=email, password=password)
        
        token = token_glob['token']
        expiration = token_glob['expiration']
        #if success
        if token:
            #save them in the DB
            u = User.create_or_update(name=name, 
                                        email=email, 
                                        token=token, 
                                        token_expiration=expiration, 
                                        api_id=api_key)
            
            #This will be false if the user was never created
            u_accessor = User.update_accessor(u.id)
            #put the id in the session
            session[USER_SESSION_KEY] = u.id
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
        token = None
        #attempt to login to the API
        if api_key == PAG_KEY:
            token = api.login(email=email, password=password)
        else:
            token = api.login()
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
