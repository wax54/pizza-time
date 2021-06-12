from api.utils import request_with_retry, get_date, get_datetime, make_date_time_from_now
import api
BASE_URL = 'https://www.sam-the-dev.com/pag_api'
LOGIN_EXTENSION = '/login'
GET_DELIVERY_EXTENSION = '/users/get_delivery'
GET_SCHEDULES_EXTENSION = '/users/get_schedules'
RE_AUTH_EXTENSION = '/users/re_authenticate'


def get_schedules(email, token, ignore=[]):

    session = request_with_retry()
    return False
    try:
        res = session.get(
            f'{BASE_URL}{GET_SCHEDULES_EXTENSION}',
            json={
                "email": email,
                "token": token,
                "ignore_codes": ignore
            })
        # no errors connecting to the server
        json = res.json()
        session.close()
        if json['status']:
            # successful login
            return json['schedules']
        else:
            # server worked, but creds didn't
            return False
    except:
        # DB Down (likely)
        session.close()
        return False


def get_delivery(email, token):
    session = request_with_retry()
    try:
        res = session.get(f'{BASE_URL}{GET_DELIVERY_EXTENSION}',
                          json={
                              "email": email,
                              "token": token
                          })
        # no errors connecting to the server
        json = res.json()
        # got result, close the session
        session.close()

        if json['status']:
            # successful login
            # if there are any orders to be had...
            if json['delivery']['orders']:
                # turn the date string into a date object
                json['delivery']['date'] = get_date(json['delivery']['date'])
                for order in json['delivery']['orders']:
                    order['num'] = int(order['num'])
            return json['delivery']
        else:
            # server worked, but creds didn't
            return False
    except:
        # DB Down (likely)
        # close the session
        session.close()
        return False
    
def token_expiry(email, token):
    return make_date_time_from_now(days=3)

def re_auth(email, token):
    session = request_with_retry()
    return False
    try:
        res = session.get(f'{BASE_URL}{RE_AUTH_EXTENSION}',
                          json={
                              "email": email,
                              "token": token
                          })
        # no errors connecting to the server
        json = res.json()
        # got result, close the session
        session.close()

        if json['status']:
            # successful revalidate
            return {"token": json['user']['token'],
                    "expiration": get_datetime(json['user']['expiration'])}
        else:
            # server worked, but creds didn't
            return False
    except:
        # DB Down (likely)
        # close the session
        session.close()
        return False


def login(email, password):

    # Harden this up. sometimes get 500 error when the server needs to unseal
    # gets 404 out of nowhere
    # maybe just retry after a second?
    session = request_with_retry()
    try:
        res = session.post(f'{BASE_URL}{LOGIN_EXTENSION}',
                           json={
                               "email": email,
                               "password": password
                           })

        # no errors connecting to the server
        json = res.json()
        session.close()
        if json['status']:
            # successful login
            return {"token": json['user']['token'], 
                    "expiration": get_datetime(json['user']['expiration'])}
        else:
            # server worked, but creds didn't
            return False
    except:
        session.close()
        return False

