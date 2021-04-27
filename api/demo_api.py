from random import randint
import datetime

DATE_FORMAT = "%a, %d %b %Y %H:%M:%S GMT"  # "Mon, 19 Apr 2021 00:00:00 GMT"


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
            return [
                {"week_code": 10121,
                    "schedule": [
                        {"start": "Mon, 19 Apr 2021 17:00:00 GMT",
                         "end": "Mon, 19 Apr 2021 21:00:00 GMT",
                         "shift_type": "DR1"},
                        {"start": "Wed, 21 Apr 2021 16:00:00 GMT",
                            "end": "Wed, 21 Apr 2021 20:00:00 GMT",
                            "shift_type": "DRRUSH"},
                        {"start": "Thu, 22 Apr 2021 17:00:00 GMT",
                            "end": "Thu, 22 Apr 2021 22:00:00 GMT",
                            "shift_type": "DR4"},
                        {"start": "Sat, 24 Apr 2021 16:00:00 GMT",
                            "end": "Sat, 24 Apr 2021 23:00:00 GMT",
                            "shift_type": "DRLATE"}
                    ]}
            ]
        else:
            return []
    else:
        return False




def get_delivery(email, token):
    if email and token:
        # successful login
        return {"orders": [{"num": 112,
                           "name": "Kassandra Meyers",
                           "address": "12525 NE 32nd St Bellevue, WA. 98005",
                            "phone": "425-155-1443"},
                           {"num": 117,
                           "name": "Bernadett Winthrop",
                            "address": "3050 125th Ave NE Bellevue, WA. 98005",
                            "phone": "425-555-8972"}],
               "date": make_date(datetime.date.today())}
    else:
        return False


def login(email, password):
    if email and password:
        # successful login
        return hash(randint(100, 100000000))
    else:
        return False
