"""Flask Notes app"""

from flask import Flask, redirect, render_template, session
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User
from forms import RegisterForm, LoginForm

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///flask_notes"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "shhh"

connect_db(app)
db.create_all()

toolbar = DebugToolbarExtension(app)

@app.get('/')
def homepage():
    """Redirect to /register route"""

    return redirect('/register')

@app.route('/register', methods=['GET', 'POST'])
def register_user():
    """Show and handle submission of form to register user"""

    form = RegisterForm()

    if form.validate_on_submit():
        new_user = User.register(
            username = form.username.data,
            password = form.password.data,
            email = form.email.data,
            first_name = form.first_name.data,
            last_name = form.last_name.data
        )

        db.session.add(new_user)
        db.session.commit()

        session['user_username'] = new_user.username

        return redirect('/secret')

    else:
        return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login_user():
    """ Show and handle submission of login form for existing user """

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(
            username = form.username.data, 
            password = form.password.data
        )

        if user:
            session['user_username'] = user.username
            return redirect('/secret')
        else:
            form.username.errors = ['Bad name/password']

    return render_template('login.html', form=form)

@app.get('/secret')
def show_secret_page():
    """ Render the top secret, logged-in-only page """

    return ("You made it!")