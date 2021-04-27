from db_setup import db
import datetime


class User(db.Model):
    """A single user"""
    __tablename__ = "users"
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.Text, unique=True)
    email = db.Column(db.Text, nullable=False)
    token = db.Column(db.Text, nullable=False, unique=True)
    shifts = db.relationship('Schedule',
                             backref='user')

    @classmethod
    def get(cls, pk):
        return cls.query.get(pk)

    @classmethod
    def create_or_update(cls, email, token, name=None):
        """If a user already exists, update the token (and name if given) 
        and return the id to the caller
            otherwise, create the user and return the id to the caller"""
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


class Schedule(db.Model):
    """A single shift"""
    __tablename__ = "schedules"
    id = db.Column(
        db.Integer, autoincrement=True, primary_key=True)
    start = db.Column(db.DateTime, nullable=False)
    end = db.Column(db.DateTime, nullable=False)
    shift_type = db.Column(db.String(20))
    user_id = db.Column(db.Integer, db.ForeignKey(
        'users.id', ondelete='CASCADE'))

    def get_shift_length(self):
        """gets the length of the shift
        returns a datetime.timedelta object """
        return self.end-self.start

    @classmethod
    def get_future_shifts(cls, user_id):
        return cls.query.filter(
            Schedule.user_id == user_id,
            Schedule.start >= datetime.date.today()
        ).all()

    @classmethod
    def get_last(cls, user_id, delta=None):
        if delta:
            return cls.query.filter(
                Schedule.user_id == user_id,
                Schedule.start <= datetime.date.today(),
                Schedule.end >= (datetime.date.today() - delta)

            ).all()
        else:
            return cls.query.filter(
                Schedule.user_id == user_id,
                Schedule.start <= datetime.date.today()

            ).all()

    @classmethod
    def add_from_pag(cls, schedules, user_id):

        for week in schedules:
            # for each week in schedules,
            # add the pag_code to WeekCode
            code = week['pag_code']
            WeekCode.add(code, user_id)
            for shift in week['schedule']:
                # for every shift, make a new schedule
                db_shift = Schedule(
                    start=shift['start'],
                    end=shift['end'],
                    shift_type=shift['shift_type'],
                    user_id=user_id)
                db.session.add(db_shift)
        db.session.commit()

    @classmethod
    def add_from_demo(cls, schedules, user_id):

        for week in schedules:
            # for each week in schedules,
            # add the week_code to WeekCode
            code = week['week_code']
            WeekCode.add(code, user_id)
            for shift in week['schedule']:
                # for every shift, make a new schedule
                db_shift = Schedule(
                    start=shift['start'],
                    end=shift['end'],
                    shift_type=shift['shift_type'],
                    user_id=user_id)
                db.session.add(db_shift)
        db.session.commit()


# def get_datetime(string_date):
#     DATE_FORMAT = "%a, %d %b %Y %H:%M:%S %Z"  # "Mon, 19 Apr 2021 00:00:00 GMT"
#     return datetime.datetime.strptime(string_date, DATE_FORMAT)


class WeekCode(db.Model):
    __tablename__ = "week_codes"
    code = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(
        'users.id', ondelete='CASCADE'))

    @classmethod
    def add(cls, code, user_id):
        db_entry = cls(code=code, user_id=user_id)
        db.session.add(db_entry)
        db.session.commit()

    @classmethod
    def get_codes_for_user(cls, user_id):
        return cls.query.filter_by(user_id=user_id).limit(3).all()
