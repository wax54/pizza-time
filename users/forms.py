"""forms involving the User Class"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField
from wtforms.validators import InputRequired, Optional
from api import PAG_KEY, DEMO_KEY


class UserLogin(FlaskForm):
    email = StringField('Email', validators=[
        InputRequired(message='Email Cannot Be Blank!')])
    password = PasswordField('Password', validators=[
                             InputRequired(message='Password Cannot Be Blank!')])
    api = SelectField(
        'API', choices=[(DEMO_KEY, 'Demo'), (PAG_KEY, 'Pagliacci')])


class DemoUserLogin(FlaskForm):
    name = StringField('Name', validators=[
        InputRequired(message='Name Cannot Be Blank!')])



class PagUserLogin(FlaskForm):
    name = StringField('Name(optional)', validators=[Optional()])
    email = StringField('Email', validators=[
        InputRequired(message='Email Cannot Be Blank!')])
    password = PasswordField('Password', validators=[
                             InputRequired(message='Password Cannot Be Blank!')])
