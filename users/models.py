
from api.utils import make_date_time_from_now
from db_setup import db
import secrets
import datetime



class User(db.Model):
    """A single user"""
    __tablename__ = "users"
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.Text)
    email = db.Column(db.Text, nullable=False)
    token = db.Column(db.Text, nullable=False, unique=True)
    token_expiration = db.Column(db.DateTime, nullable=True)
    accessor = db.Column(db.Text, nullable=True)
    accessor_expiration = db.Column(db.DateTime, nullable=True)
    api_id = db.Column(db.Text, nullable=False)
    shifts = db.relationship('Schedule',
                             backref='user')

    @classmethod
    def get(cls, pk):
        """a shortcut for the cls.query.get() function"""
        return cls.query.get(pk)

    @classmethod
    def get_by_accessor(cls, accessor):
        """gets a user by its accessor"""
        user = cls.query.filter_by(accessor=accessor).first()
        return user if user else False
    
    @classmethod
    def update_accessor(cls, id):
        """updates a users accessor by id"""
        user = cls.get(id)
        if not user:
            return False
        accessor_blob = cls.create_unique_accessor()
        user.accessor = accessor_blob['accessor']
        user.accessor_expiration = accessor_blob['expiration']
        
        db.session.add(user)
        db.session.commit()
        
        return accessor_blob['accessor']

    @classmethod
    def delete_by_email(cls, email):
        """A quick way of deleting a user by email"""
        cls.query.filter_by(email=email).delete()
        db.session.commit()

    @classmethod
    def create(cls, email, token, api_id, token_expiration=None,  name=None):
        u = User(email=email, token=token, token_expiration=token_expiration, name=email, api_id=api_id)
        if name:
            u.name = name
        db.session.add(u)
        db.session.commit()
        return u
    
    @classmethod
    def create_or_update(cls, email, token, api_id, token_expiration=None, name=None):
        """If a user with this email already exists, update the token (and name if given) 
        and return the id to the caller
            otherwise, create the user and return the id to the caller"""
        u = cls.query.filter_by(email=email).first()
        
        if u:
            # user already exists, just update token
            u.token = token
        else:
            u = User(email=email, token=token, name=email, api_id=api_id)

        if name:
            u.name = name
            
        if token_expiration:
            u.token_expiration = token_expiration

        db.session.add(u)
        db.session.commit()
        return u
    
    @classmethod
    def create_unique_accessor(cls):
        ACCESSOR_TIMEOUT_DAYS = 8
        
        accessor = secrets.token_urlsafe()
        
        while cls.get_by_accessor(accessor):
            accessor = secrets.token_urlsafe()
            
        expiration = make_date_time_from_now(days=ACCESSOR_TIMEOUT_DAYS)
        
        return {"accessor": accessor, "expiration": expiration}



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


    def get_shift_hours(self):
        """gets the length of the shift in hours """
        
        delta = self.get_shift_length()
        # 60 seconds in a min, 60 mins in a hour
        return delta.total_seconds() / 60 / 60

    @classmethod
    def get_future_shifts(cls, user_id):
        """returns a list of shifts for user_id 
        that end on or after today"""
        #get a timestamp for the beginning of the day
        today = datetime.date.today()
        return cls.query.filter(
            Schedule.user_id == user_id,
            Schedule.end >= today
        ).order_by(Schedule.start).all()

    @classmethod
    def get_last(cls, user_id, delta=None):
        """returns a list of shifts for user_id that start on or before today
        optionally the delta param further limits the results to shits that end on or after 
        today - delta"""
        #get a timestamp at the end of the day
        today = datetime.datetime.today() + datetime.timedelta(hours=11, minutes=59)
        if delta:
            return cls.query.filter(
                Schedule.user_id == user_id,
                Schedule.start <= today,
                Schedule.end >= (datetime.date.today() - delta)

            ).all()
        else:
            return cls.query.filter(
                Schedule.user_id == user_id,
                Schedule.start <= today

            ).all()

    @classmethod
    def add_from_pag(cls, schedules, user_id):
        """adds a list of schedules from the pag api"""
        #weeks that are already in the DB
        used_codes = WeekCode.get_codes_for_user(user_id, limit=10)
        for week in schedules:
            
            code = week['pag_code']
            if int(code) not in used_codes:
                # for each week in schedules,
                # add the pag_code to WeekCode
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
        """adds a list of schedules from the demo api"""
        used_codes = WeekCode.get_codes_for_user(user_id, limit=10)
        for week in schedules:
            # for each week in schedules,
            # add the week_code to WeekCode
            code = week['week_code']
            if int(code) not in used_codes:
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


class WeekCode(db.Model):
    """represets one week of data(so we don't write the same week twice)"""
    __tablename__ = "week_codes"
    code = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(
        'users.id', ondelete='CASCADE'), primary_key=True)

    @classmethod
    def add(cls, code, user_id):
        """add a code to the db"""
        db_entry = cls(code=code, user_id=user_id)
        db.session.add(db_entry)
        try:
            db.session.commit()
            return True
        except:
            return False

    @classmethod
    def get_codes_for_user(cls, user_id, limit = 8):
        """gets the codes for a specified user. defaults to limiting to 3"""
        week_codes = cls.query.filter_by(user_id=user_id).order_by(
            cls.code.desc()).limit(limit).all()
        return [w.code for w in week_codes]
