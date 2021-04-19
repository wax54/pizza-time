"""forms involving the User Class"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired


class PagUserLogin(FlaskForm):
    email = StringField('Email', validators=[
        InputRequired(message='Email Cannot Be Blank!')])
    password = PasswordField('Password', validators=[
                             InputRequired(message='Password Cannot Be Blank!')])
