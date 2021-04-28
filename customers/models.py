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
            if address:
                customer.address = address
            if phone:
                customer.phone = phone
        else:
            customer = cls(id=id, name=name, address=address, phone=phone)
        db.session.add(customer)
        db.session.commit()
        return customer
