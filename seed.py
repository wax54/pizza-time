from app import db
from users.models import User, Schedule
from deliveries.models import Delivery, Order, Customer
db.drop_all()
db.create_all()

user = {
    "email": "fake@fake.com",
    "token": "faketoken",
    "name": "John Bogus"
}

customer = {
    "name": "Martha Jones"
}

deliveries = [{"driver_id": 1},
              {"driver_id": 1},
              {"driver_id": 1},
              {"driver_id": 1},
              {"driver_id": 1},
              {"driver_id": 1}]
orders = [{
    "id": '2021-04-15|213',
    "date": '2021-04-15',
    "tip": 10,
    "del_id": 1,
    "cust_id": 1,
    "driver_id": 1}, 
          {
    "id": '2021-04-15|218',
    "date": '2021-04-15',
    "tip": 3,
    "del_id": 1,
    "cust_id": 1,
    "driver_id": 1}, 
          {
    "id": '2021-04-15|230',
    "date": '2021-04-15',
    "tip": 5,
    "del_id": 2,
    "cust_id": 1,
    "driver_id": 1}, 
          {
    "id": '2021-04-16|103',
    "date": '2021-04-16',
    "tip": 5,
    "del_id": 3,
    "cust_id": 1,
    "driver_id": 1}, 
          {
    "id": '2021-04-18|116',
    "date": '2021-04-18',
    "tip": 5,
    "del_id": 4,
    "cust_id": 1,
    "driver_id": 1}, 
          {
    "id": '2021-04-18|213',
    "date": '2021-04-18',
    "tip": 5,
    "del_id": 5,
    "cust_id": 1,
    "driver_id": 1}, 
          {
    "id": '2021-04-20|101',
    "date": '2021-04-20',
    "tip": 5,
    "del_id": 6,
    "cust_id": 1,
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
