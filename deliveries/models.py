from db_setup import db
from deliveries.utils import get_date


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
        date = get_date(delivery['date'])
        orders = delivery['orders']
        old_deliveries = set()

        delivery = Delivery(date=date, driver_id=driver_id)
        db.session.add(delivery)
        db.session.commit()
        ######
        # A little wasteful, good optimization possibility, I think
        for order in orders:
            o_id = Order.make_id_from_date_and_num(
                date=date, num=order['num'])
            o = Order.query.get(o_id)
            if o:
                old_deliveries.add(o.del_id)
                o.del_id = delivery.id
                o.driver_id = driver_id
            else:
                # maybe change this to a hash of the phone and address
                c = Customer.create_or_get(name=order['phone'])
                o = Order(
                    id=o_id,
                    del_id=delivery.id,
                    cust_id=c.id,
                    driver_id=driver_id)
            db.session.add(o)
        db.session.commit()

        Delivery.dispose_of_empty_dels(old_deliveries)
        return delivery

    @classmethod
    def dispose_of_empty_dels(cls, del_ids):
        for del_id in del_ids:
            d = cls.query.get(del_id)
            if len(d.orders) == 0:
                db.session.delete(d)
        db.session.commit()


class Order(db.Model):
    """A single order"""
    __tablename__ = "orders"
    id = db.Column(db.Text, primary_key=True)
    tip = db.Column(db.Float, server_default='0')
    del_id = db.Column(db.Integer, db.ForeignKey(
        'deliveries.id', ondelete='CASCADE'))
    cust_id = db.Column(db.Integer, db.ForeignKey(
        'customers.id', ondelete='SET NULL'))
    driver_id = db.Column(db.Integer, db.ForeignKey(
        'users.id', ondelete='CASCADE'))

    @classmethod
    def search(cls, date, num):
        id = cls.get_id_from_date_and_num(date=date, num=num)
        o = cls.query.get(id)
        if o:
            return o
        else:
            return False

    @classmethod
    def make_id_from_date_and_num(cls, date, num):
        return f'{date}{num}'


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