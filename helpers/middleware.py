from flask import g, request, redirect
from config import RENEWAL_TIMEFRAME, JWT_AUTH_KEY
from users.models import User

import tz_utils
import pytz

def update_token():
    token = g.user.token
    email = g.user.email
    #token is expired, do something!
    new_token_glob = g.api.re_auth(email=email, token=token)

    if(new_token_glob):
        new_token = new_token_glob['token']
        expiration = new_token_glob['expiration']
        g.user.update_token(token=new_token,
                            token_expiration=expiration)
    else:
        print(f'failed fetching token for user {g.user.id}')


def keep_api_token_up_to_date():
    #assumed token expiration is in UTC
    token_expiration = g.user.token_expiration
    if not token_expiration:
        return update_token()
    token_expiration = pytz.utc.localize(token_expiration)

    if (token_expiration - tz_utils.get_now_in(tz='UTC')) < RENEWAL_TIMEFRAME:
        return update_token


def keep_user_accessor_up_to_date(response):
    if g.user:
        curr_expiration = g.user.accessor_expiration
        curr_expiration = pytz.utc.localize(curr_expiration)
        # seeing if the accessor has less than RENEWAL_TIMEFRAME TTL
        if (curr_expiration - tz_utils.get_now_in(tz='UTC')) < RENEWAL_TIMEFRAME:
            #accessor is expired!
            g.user.update_accessor()
            user_jwt = g.user.make_jwt()
            # put the auth in the cookies
            response.set_cookie(JWT_AUTH_KEY, user_jwt,
                                expires=g.user.accessor_expiration)
    return response


def ensure_logged_in():
    """If we're logged in, add curr user to Flask global.
    otherwise, redirect them to login"""
    # if USER_SESSION_KEY in session:
    if g.user:
        return True
    else:
        return False


#If a user_jwt is in the cookies, try to add that user to g
#otherwise, just move along
def add_user_to_g():
    #TODO double check that request.cookies is a dict of the cookies on the request
    if JWT_AUTH_KEY in request.cookies:
        try:
            user_jwt = request.cookies[JWT_AUTH_KEY]
            g.user = User.authenticate(user_jwt)
        except:
            g.user = None
    else:
        g.user = None


#HTTPS ONLY
def https_redirect():
    if request.headers.get('X-Forwarded-Proto') == 'http':
        url = request.url.replace('http://', 'https://')
        return redirect(url)
