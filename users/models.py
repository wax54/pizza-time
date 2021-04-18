from db_setup import db


class User(db.Model):
    """A single user"""
    __tablename__ = "users"
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.Text, nullable=False, unique=True)
    username = db.Column(db.Text, nullable=False)
    token = db.Column(db.Text, nullable=False, unique=True)


class Customer(db.Model):
    """A single user"""
    __tablename__ = "users"
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    identifier = db.Column(db.Text, nullable=False, unique=True)
    username = db.Column(db.Text, nullable=False)
    token = db.Column(db.Text, nullable=False, unique=True)
