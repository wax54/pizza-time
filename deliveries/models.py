from db_setup import db


class Delivery(db.Model):
    """A single delivery"""
    __tablename__ = "deliveries"
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    driver_id = db.Column(db.Integer, db.ForeignKey(
        'users.id', ondelete='CASCADE'))
    orders = db.relationship('Order',
                             backref='delivery')

    @classmethod
    def save_delivery(cls, delivery, driver_id):
        print(delivery)
        date = delivery['date']
        orders = delivery['orders']
        old_deliveries = set()

        delivery = Delivery(date=date, driver_id=driver_id)
        db.session.add(delivery)
        db.session.commit()

        for order in orders:
            o = Order.search(date=date, num=order["num"])
            if o:
                old_deliveries.add(o.del_id)
                o.del_id = delivery.id
                o.driver_id = driver_id
            else:
                #maybe change this to a hash of the phone and address
                c = Customer.create_or_get(name=order['phone'])
                o = Order(
                    date=date, num=order['num'], del_id=delivery.id, cust_id=c.id, driver_id=driver_id)
            db.session.add(o)
        db.session.commit()

        Delivery.dispose_of_empty_dels(old_deliveries)
        return delivery

    @classmethod
    def dispose_of_empty_dels(cls, del_ids):
        for del_id in del_ids:
            d = cls.query.get(del_id)
            if len(d.orders) == 0:
                cls.query.delete(del_id)
        db.session.commit()


class Order(db.Model):
    """A single order"""
    __tablename__ = "orders"
    id = db.Column(
        db.Integer, autoincrement=True, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    num = db.Column(db.Integer, nullable=False)
    tip = db.Column(db.Float, server_default='0')
    del_id = db.Column(db.Integer, db.ForeignKey(
        'deliveries.id', ondelete='CASCADE'))
    cust_id = db.Column(db.Integer, db.ForeignKey(
        'customers.id', ondelete='SET NULL'))
    driver_id = db.Column(db.Integer, db.ForeignKey(
        'users.id', ondelete='CASCADE'))

    @classmethod
    def search(cls, date, num):
        o = cls.query.filter_by(date=date, num=num).first()
        if o:
            return o
        else:
            return False


class Customer(db.Model):
    """A single customer"""
    __tablename__ = "customers"
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    notes = db.relationship('Note',
                            backref='customer')

    @classmethod
    def create_or_get(cls, name):
        c = cls.query.filter_by(name=name).first()
        if c:
            return c
        else:
            c = cls(name=name)
            db.session.add(c)
            db.session.commit()
            return c


class Note(db.Model):
    """A single note"""
    __tablename__ = "notes"
    cust_id = db.Column(db.Integer, db.ForeignKey(
        'customers.id', ondelete='CASCADE'), primary_key=True)
    driver_id = db.Column(db.Integer, db.ForeignKey(
        'users.id', ondelete='CASCADE'), primary_key=True)
    note = db.Column(db.Text, nullable=False)
