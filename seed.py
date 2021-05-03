from app import db
from users.models import User, Schedule
from deliveries.models import Delivery, Order, Customer
from api import DEMO_KEY
db.drop_all()
db.create_all()

user = {
    "email": "demo_user",
    "token": "faketoken",
    "name": "John Bogus",
    "api_id": DEMO_KEY
}

cust_id = Customer.make_id_from_phone("425-555-7843")
customer = {
    "id":  cust_id,
    "name": "Martha Jones"
}

deliveries = [{"driver_id": 1},
              {"driver_id": 1},
              {"driver_id": 1},
              {"driver_id": 1},
              {"driver_id": 1},
              {"driver_id": 1}]

orders = [{
    "num": '213',
    "date": '2021-04-15',
    "tip": 10,
    "del_id": 1,
    "cust_id": cust_id,
    "driver_id": 1},
    {
    "num": '218',
    "date": '2021-04-15',
    "tip": 3,
    "del_id": 1,
    "cust_id": cust_id,
    "driver_id": 1},
    {
    "num": '230',
    "date": '2021-04-15',
    "tip": 5,
    "del_id": 2,
    "cust_id": cust_id,
    "driver_id": 1},
    {
    "num": '103',
    "date": '2021-04-16',
    "tip": 5,
    "del_id": 3,
    "cust_id": cust_id,
    "driver_id": 1},
    {
    "num": '116',
    "date": '2021-04-18',
    "tip": 5,
    "del_id": 4,
    "cust_id": cust_id,
    "driver_id": 1},
    {
    "num": '213',
    "date": '2021-04-18',
    "tip": 5,
    "del_id": 5,
    "cust_id": cust_id,
    "driver_id": 1},
    {
    "num": '101',
    "date": '2021-04-20',
    "tip": 5,
    "del_id": 6,
    "cust_id": cust_id,
    "driver_id": 1}]

schedules = [
    {"start": "Mon, 19 Apr 2021 17:00:00 GMT",
     "end": "Mon, 19 Apr 2021 21:00:00 GMT",
     "shift_type": "DR1",
     "user_id": 1},
    {"start": "Wed, 21 Apr 2021 16:00:00 GMT",
     "end": "Wed, 21 Apr 2021 20:00:00 GMT",
     "shift_type": "DRRUSH",
     "user_id": 1},
    {"start": "Thu, 22 Apr 2021 17:00:00 GMT",
     "end": "Thu, 22 Apr 2021 22:00:00 GMT",
     "shift_type": "DR4",
     "user_id": 1},
    {"start": "Sat, 24 Apr 2021 16:00:00 GMT",
     "end": "Sat, 24 Apr 2021 23:00:00 GMT",
     "shift_type": "DRLATE",
     "user_id": 1}
]

u = User(**user)
db.session.add(u)
db.session.commit()

for delivery in deliveries:
    d = Delivery(**delivery)
    db.session.add(d)
c = Customer(**customer)

db.session.add(d)
db.session.add(c)
db.session.commit()

for order in orders:
    o = Order(**order)
    db.session.add(o)
db.session.commit()

for shift in schedules:
    # for every shift, make a new schedule
    db_shift = Schedule(**shift)
    db.session.add(db_shift)
    db.session.commit()


# add a 'demo_user' user and add a note to the demo api order customer so the 
#    person using the demo can see what a note left by another driver looks like
