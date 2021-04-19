from db_setup import db


class User(db.Model):
    """A single user"""
    __tablename__ = "users"
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.Text, unique=True)
    email = db.Column(db.Text, nullable=False)
    token = db.Column(db.Text, nullable=False, unique=True)
    notes = db.relationship('Note',
                            backref='user')

    @classmethod
    def get(cls, pk):
        return cls.query.get(pk)

    @classmethod
    def create_or_update(cls, email, token, name=None):
        u = cls.query.filter_by(email=email).first()
        if u:
            # user already exists, just update token
            u.token = token
        else:
            u = User(email=email, token=token, name=email)

        if name:
            u.name = name
        db.session.add(u)
        db.session.commit()
        return u.id


class schedules(db.Model):
    """A single shift"""
    __tablename__ = "schedules"
    id = db.Column(
        db.Integer, autoincrement=True, primary_key=True)
    pag_code = db.Column(db.Integer, nullable=False)
    start = db.Column(db.DateTime, nullable=False)
    end = db.Column(db.DateTime, nullable=False)
    shift_type = db.Column(db.String(20))
    user_id = db.Column(db.Integer, db.ForeignKey(
        'users.id', ondelete='CASCADE'))
