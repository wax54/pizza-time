from random import randint
import datetime
import tz_utils

DATE_FORMAT = "%a, %d %b %Y %H:%M:%S GMT"  # "Mon, 19 Apr 2021 00:00:00 GMT"

DEMO_DELIVERY = {"orders": [{"num": 112,
                             "name": "Kassandra Meyers",
                             "address": "202 Waterwood Bend, Peachtree City",
                            "phone": "425-155-1443"},
                            {"num": 117,
                            "name": "Bernadett Winthrop",
                             "address": "103 Pine Cone Break, Peachtree City",
                             "phone": "425-555-8972"}],
                 "date": datetime.date.today()}

def make_date_time_from_now(days=0, hours=0):
    """a function that returns a string 
    representing a time that is 'days' days 
    and 'hours' hours away from now"""
    
    now = tz_utils.get_now_in()
    date_time = now + datetime.timedelta(days=days, hours=hours)
    return date_time.strftime(DATE_FORMAT)
    

DEMO_SCHEDULES = [
    {"week_code": 10121,
     "schedule": [
         {"start": make_date_time_from_now(hours=-1),
          "end": make_date_time_from_now(hours=5),
          "shift_type": "DR1"},
         {"start": make_date_time_from_now(days=1,hours=-1), 
          "end": make_date_time_from_now(days=1, hours=8),
          "shift_type": "DRRUSH"},
         {"start": make_date_time_from_now(days=3, hours=-1),
          "end": make_date_time_from_now(days=3, hours=3),
          "shift_type": "DR4"},
         {"start": make_date_time_from_now(days=5, hours=-1),
          "end": make_date_time_from_now(days=5, hours=6),
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
    return date.strftime(DATE_FORMAT)

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


def login(email, password):
    if email and password:
        # successful login
        return hash(randint(100, 100000000))
    else:
        return False
