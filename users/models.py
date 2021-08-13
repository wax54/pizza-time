
from os import access
from config import SECRET_KEY, ACCESSOR_SESSION_KEY,  USER_SESSION_KEY, API_SESSION_KEY
from api.utils import make_date_time_from_now
from db_setup import db
from flask_bcrypt import Bcrypt
import secrets
import datetime
import jwt

bcrypt = Bcrypt()


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
    def make_jwt(self):
        #JWT payload looks like {ACCESSOR_SESSION_KEY: accessor, USER_SESSION_KEY: u.id}
        return jwt.encode({
            ACCESSOR_SESSION_KEY: self.accessor,
            USER_SESSION_KEY: self.id
        },
            SECRET_KEY,
            algorithm="HS256")
        
    def update_token(self, token, token_expiration):
        """updates a users token"""

        self.token = token
        self.token_expiration = token_expiration
        db.session.add(self)
        db.session.commit()


    def update_accessor(self):
        """updates a users accessor"""
        ACCESSOR_TIMEOUT_DAYS = 4
        
        accessor = User.create_unique_accessor()
        self.accessor = accessor

        expiration = make_date_time_from_now(days=ACCESSOR_TIMEOUT_DAYS)
        self.accessor_expiration = expiration

        db.session.add(self)
        db.session.commit()
        # unneccesary
        # #use bcrypt to hash the accessor
        # hashed = bcrypt.generate_password_hash(user.accessor)
        # # turn bytestring into normal (unicode utf8) string
        # hashed_utf8 = hashed.decode("utf8")

        return self.accessor

    @classmethod
    def get(cls, pk):
        """a shortcut for the cls.query.get() function"""
        return cls.query.get(pk)


    @classmethod
    def authenticate(cls, user_jwt):
        """gets a user by its accessor"""
        user_data = jwt.decode(user_jwt, SECRET_KEY, algorithms="HS256")

        accessor = user_data[ACCESSOR_SESSION_KEY]
        u_id = user_data[USER_SESSION_KEY]
        user = cls.get(u_id)
        if user:
            if user.accessor == accessor:
                return user
            else:
                return False
        else:
            return False

    @classmethod
    def get_by_accessor(cls, accessor):
        """gets a user by its accessor"""
        user = cls.query.filter_by(accessor=accessor).first()
        return user if user else False
    

    @classmethod
    def delete_by_email(cls, email):
        """A quick way of deleting a user by email"""
        cls.query.filter_by(email=email).delete()
        db.session.commit()

    @classmethod
    def create(cls, email, token, api_id, token_expiration=None,  name=None):
        user = User(email=email, token=token, token_expiration=token_expiration, name=email, api_id=api_id)
        if name:
            user.name = name
        db.session.add(user)
        db.session.commit()
        user.update_accessor()

        return user
    
    @classmethod
    def create_or_update(cls, email, token, api_id, token_expiration=None, name=None):
        """If a user with this email already exists, update the token (and name if given) 
        and return the id to the caller
            otherwise, create the user and return the id to the caller"""
        user = cls.query.filter_by(email=email).first()
        
        if user:
            # user already exists, just update token
            user.token = token
        else:
            user = User(email=email, token=token, name=email, api_id=api_id)

        if name:
            user.name = name
            
        if token_expiration:
            user.token_expiration = token_expiration

        db.session.add(user)
        db.session.commit()
        user.update_accessor()
        
        return user
    
    @classmethod
    def create_unique_accessor(cls):
        accessor = secrets.token_urlsafe()
        
        while cls.get_by_accessor(accessor):
            accessor = secrets.token_urlsafe()
            
        return accessor



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
