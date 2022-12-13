from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Email, length


class RegisterForm(FlaskForm):
    """Form for registering a user."""

    username = StringField("Username", validators=[InputRequired(), length(max=20)])
    password = PasswordField("Password", validators=[InputRequired(), length(max=100)])
    email = StringField('Email', validators=[Email(), length(max=50)])
    first_name = StringField('First Name', validators=[InputRequired(), length(max=30)])
    last_name = StringField('Last Name', validators=[InputRequired(), length(max=30)])

class LoginForm(FlaskForm):
    """ Form for loging in a user. """

    username = StringField("Username", validators=[InputRequired(), length(max=20)])
    password = PasswordField("Password", validators=[InputRequired(), length(max=100)])

class CSRFProtectForm(FlaskForm):
    """ CSRF-only form for logging out a user """

    