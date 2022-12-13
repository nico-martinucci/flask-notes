from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, length, Email


class RegisterForm(FlaskForm):
    """Form for registering a user."""

    username = StringField("Username", validators=[InputRequired(), length(max=20)])
    password = PasswordField("Password", validators=[InputRequired(), length(max=100)])
    email = StringField('Email', validators=[Email(), length(max=50)])
    first_name = StringField('First Name', validators=[InputRequired(), length(max=30)])
    last_name = StringField('First Name', validators=[InputRequired(), length(max=30)])