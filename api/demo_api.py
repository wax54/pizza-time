from random import randint


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
        return{"orders": [{"num": randint(100, 380),
                           "name": "Kassandra Meyers",
                           "address": "12527 NE 32nd St Bellevue, WA. 98005",
                           "phone": "425-155-1443"}],
               "date": "Mon, 19 Apr 2021 00:00:00 GMT"}
    else:
        return False


def login(email, password):
    if email and password:
        # successful login
        return hash(randint(100, 100000000))
    else:
        return False
