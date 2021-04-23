from random import randint

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
        return "DEMOUSERTOKEN"
    else:
        return False
