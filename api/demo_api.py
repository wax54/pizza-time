from random import randint
from api.utils import string_date_time, make_date_time_from_now
import datetime
DATE_FORMAT = "%a, %d %b %Y %H:%M:%S %Z"  # "Mon, 19 Apr 2021 00:00:00 GMT"

DEMO_DELIVERY = {"orders": [{"num": 43,
                             "name": "Kassandra Meyers",
                             "address": "12704 NE 88th Ln, Kirkland, WA 98033",
                            "phone": "425-155-1443"},
                            {"num": 17,
                            "name": "Gracy Williams",
                             "address": "10035 127th Ave NE, Kirkland, WA 98033",
                             "phone": "425-555-8972"}],
                 "date": string_date_time(
                     make_date_time_from_now().date()),
                 "store": "1"}


DEMO_SCHEDULES = [
    {"week_code": 10121,
     "schedule": [
         {"start": string_date_time(make_date_time_from_now(hours=-1)),
          "end": string_date_time(make_date_time_from_now(hours=5)),
          "shift_type": "DR1"},
         {"start": string_date_time(make_date_time_from_now(days=1,hours=-2)), 
          "end": string_date_time(make_date_time_from_now(days=1, hours=8)),
          "shift_type": "DRRUSH"},
         {"start": string_date_time(make_date_time_from_now(days=3, hours=1)),
          "end": string_date_time(make_date_time_from_now(days=3, hours=3)),
          "shift_type": "DR4"},
         {"start": string_date_time(make_date_time_from_now(days=5, hours=-1)),
          "end": string_date_time(make_date_time_from_now(days=5, hours=6)),
          "shift_type": "DRLATE"}
     ]}
]

def order_num_generator():
    while(True):
        a = 100
        while(a < 999):
            yield a
            a += 1


order_num = order_num_generator()

def make_date(date):
    return datetime.date.strftime(DATE_FORMAT)

def get_schedules(email, token, ignore=[]):
    if email and token:
        if 10121 in ignore:
            return []
        else:
            return DEMO_SCHEDULES
    else:
        return False




def get_delivery(email, token):
    if email and token:
        # successful login
        return DEMO_DELIVERY
    else:
        return False

def token_expiry(email, token):
    return make_date_time_from_now(days=4)


def re_auth(email, token):
    return {"token": hash(randint(100, 100000000)), "expiration": make_date_time_from_now(years=1)}


def login(email='', password=''):
    # successful login
    return {"token": hash(randint(100, 100000000)), "expiration": make_date_time_from_now(years=1)}
