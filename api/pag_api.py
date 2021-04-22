from api.utils import request_with_retry

BASE_URL = 'https://www.sam-the-dev.com/pag_api'
LOGIN_EXTENSION = '/login'
GET_DELIVERY_EXTENSION = '/users/get_delivery'
GET_SCHEDULES_EXTENSION = '/users/get_schedules'


def get_schedules(email, token, ignore=[]):
    try:
        res = request_with_retry().get(f'{BASE_URL}{GET_SCHEDULES_EXTENSION}',
                                       json={
                                           "email": email,
                                           "token": token,
                                           "ignore_codes": ignore
                                       })
        # no errors connecting to the server
        json = res.json()

        if json['status']:
            # successful login
            return json['schedules']
        else:
            # server worked, but creds didn't
            return False
    except Exception as x:
        # DB Down (likely)
        return False


def get_delivery(email, token):
    try:
        res = request_with_retry().get(f'{BASE_URL}{GET_DELIVERY_EXTENSION}',
                                       json={
                                           "email": email,
                                           "token": token
                                       })
        # no errors connecting to the server
        json = res.json()
        if json['status']:
            # successful login
            return json['delivery']
        else:
            # server worked, but creds didn't
            return False
    except:
        # DB Down (likely)
        return False


def login(email, password):
    # Harden this up. sometimes get 500 error when the server needs to unseal
    # gets 404 out of nowhere
    # maybe just retry after a second?
    try:
        res = request_with_retry().post(f'{BASE_URL}{LOGIN_EXTENSION}',
                                        json={
                                            "email": email,
                                            "password": password
                                        })

        # no errors connecting to the server
        json = res.json()
        if json['status']:
            # successful login
            return json['user']['token']
        else:
            # server worked, but creds didn't
            return False
    except:
        return False
