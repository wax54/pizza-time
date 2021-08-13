from db_setup import db
from users.models import User
from customers.models import Customer
from datetime import date as date_class



class Delivery(db.Model):
    """A single delivery"""
    __tablename__ = "deliveries"
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    driver_id = db.Column(db.Integer, db.ForeignKey(
        'users.id', ondelete='CASCADE'))
    driver = db.relationship('User',
                             backref='deliveries')
    orders = db.relationship('Order',
                             backref='delivery')

    @classmethod
    def save_delivery(cls, delivery, driver_id, api_id):
        date = delivery['date']
        store = delivery['store']
        orders = delivery['orders']
        old_deliveries = set()

        delivery = Delivery(driver_id=driver_id)
        db.session.add(delivery)
        db.session.commit()
        ######
        # A little wasteful, good optimization possibility, I think
        for order in orders:
            # maybe change this to a hash of the phone and address
            customer_id = Customer.make_id_from_phone(order['phone'])
            customer = Customer.create_or_get(
                id=customer_id, name=order['name'].split(' ')[0])

            db_order = Order.get(order['num'], date, store, api_id)
            if db_order:
                old_deliveries.add(db_order.del_id)
                db_order.del_id = delivery.id
                db_order.driver_id = driver_id
                db_order.cust_id = customer_id
            else:
                db_order = Order(
                    num=order['num'],
                    date=date,
                    store=store,
                    api_id=api_id,
                    del_id=delivery.id,
                    cust_id=customer_id,
                    driver_id=driver_id)
            db.session.add(db_order)
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
    id = db.Column(db.Integer, primary_key=True)
    
    num = db.Column(db.Integer)
    date = db.Column(db.Date)
    store = db.Column(db.Text)
    api_id = db.Column(db.Text)
    
    tip = db.Column(db.Float, server_default='0')
    del_id = db.Column(db.Integer, db.ForeignKey(
        'deliveries.id', ondelete='CASCADE'))
    cust_id = db.Column(db.String(32), db.ForeignKey(
        'customers.id', ondelete='SET NULL'))
    driver_id = db.Column(db.Integer, db.ForeignKey(
        'users.id', ondelete='CASCADE'))
    driver = db.relationship('User',
                             backref='orders')
    customer = db.relationship('Customer',
                               backref='orders')

    def serialize(self):
        return {"id": self.id,
                "num": self.num,
                "tip": self.tip,
                "date": self.date,
                "del_id": self.del_id,
                "cust_id": self.cust_id,
                "driver_id": self.driver_id,
                "store": self.store,
                "api_id": self.api_id
                }

    def update_db(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def get(cls, num, date, store, api_id):
        return cls.query.filter_by(num=num, date=date, store=store, api_id=api_id).first()

    @classmethod
    def get_orders_for_day(cls, driver_id, date=date_class.today()):
        """ Returns 
        {num, tip, date, del_id, cust_id, driver_id, customer:{id, name, phone, address}
        """
        result = db.session.query(
            Order, Customer).join(
                Customer, Customer.id == Order.cust_id).filter(
                    Order.driver_id == driver_id,
                    Order.date == date).all()
        return Order.compile_orders_and_customers(result)

    @classmethod
    def get_orders_for(cls, driver_id):
        """ Returns 
        213, 04-19-21, 8425-881-7843
        """
        result = db.session.query(
            Order, Customer).join(
                Customer, Customer.id == Order.cust_id).filter(
                    Order.driver_id == driver_id).order_by(Order.date.desc(), Order.num.desc()).all()
        orders = Order.compile_orders_and_customers(result)
        orders_list = {}

        for order in orders:
            orders_for_date = orders_list.get(order['date'], [])
            orders_for_date.append(order)
            orders_list[order['date']] = orders_for_date
        return orders_list

    @classmethod
    def make_id_from_date_and_num(cls, date, num):
        return f'{date}|{num}'

    @ classmethod
    def compile_orders_and_customers(cls, order_array):
        return [{**order.serialize(), "customer": {**customer.serialize()}} for (order, customer) in order_array]
