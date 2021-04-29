from db_setup import db
from users.models import User
import hashlib


class Customer(db.Model):
    """A single customer"""
    __tablename__ = "customers"
    id = db.Column(db.String(32), primary_key=True)
    name = db.Column(db.Text)
    phone = db.Column(db.Text)
    address = db.Column(db.Text)

    def serialize(self):
        return {"id": self.id,
                "name": self.name,
                "phone": self.phone,
                "address": self.address,
                "notes": [n.serialize() for n in self.notes]
                }

    def has_note_from(self, user_id):
        for note in self.notes:
            if note.driver_id == user_id:
                return True
        return False
    @classmethod
    def make_id_from_phone(cls, phone):
        return hashlib.md5(phone.encode()).hexdigest()

    @classmethod
    def create_or_get(cls, id, name, address=None, phone=None):
        customer = cls.query.get(id)
        if customer:
            # update customer
            customer.name = name
            if address:
                customer.address = address
            if phone:
                customer.phone = phone
        else:
            customer = cls(id=id, name=name, address=address, phone=phone)
        db.session.add(customer)
        db.session.commit()
        return customer


class Note(db.Model):
    """A single note"""
    __tablename__ = "notes"
    cust_id = db.Column(db.String(32), db.ForeignKey(
        'customers.id', ondelete='CASCADE'), primary_key=True)
    driver_id = db.Column(db.Integer, db.ForeignKey(
        'users.id', ondelete='CASCADE'), primary_key=True)
    note = db.Column(db.Text, nullable=False)

    driver = db.relationship('User',
                             backref='notes')

    customer = db.relationship('Customer',
                               backref='notes')

    def serialize(self):
        return {"cust_id": self.cust_id,
                "driver_id": self.driver_id,
                "note": self.note}

    @classmethod
    def get(cls, cust_id, driver_id):
        return cls.query.get((cust_id, driver_id))

    @classmethod
    def delete(cls, cust_id, driver_id):
        note = cls.get(cust_id=cust_id, driver_id=driver_id)
        if note:
            db.session.delete(note)
            db.session.commit()
            return True
        else:
            return False

    @classmethod
    def create_or_update_note(cls, cust_id, driver_id, new_note):
        try:
            note = cls.get(cust_id=cust_id, driver_id=driver_id)
            if note:
                note.note = new_note
            else:
                note = cls(cust_id=cust_id, driver_id=driver_id, note=new_note)

            db.session.add(note)
            db.session.commit()
            return note
        except:
            db.session.rollback()
            return False
