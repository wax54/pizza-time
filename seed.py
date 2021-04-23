from app import db
from users.models import User
from deliveries.models import Delivery, Order, Customer
db.drop_all()
db.create_all()

user = {
    "id": 1,
    "email": "fake@fake.com",
    "token": "faketoken",
    "name": "John Bogus"
}

customer = {
    "id": 1,
    "name": "Martha Jones"
}

delivery = {
    "id": 1,
    "driver_id": 1
}
orders = [{
    "id": '2021-04-05|213',
    "date": '2021-04-05',
    "tip": 5,
    "del_id": 1,
    "cust_id": 1,
    "driver_id": 1}]

u = User(**user)
db.session.add(u)
db.session.commit()
d = Delivery(**delivery)
c = Customer(**customer)
db.session.add(d)
db.session.add(c)
db.session.commit()

for order in orders:
    o = Order(**order)
    db.session.add(o)
db.session.commit()
