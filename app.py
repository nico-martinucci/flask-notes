"""Flask Notes app"""

from flask import Flask, redirect, render_template, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User
from forms import RegisterForm, LoginForm, CSRFProtectForm

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///flask_notes"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "shhh"

connect_db(app)
db.create_all()

toolbar = DebugToolbarExtension(app)

SESSION_USER_KEY = 'user_username'

# add more flash messages
@app.get('/')
def homepage():
    """Redirect to /register route"""

    return redirect('/register')

@app.route('/register', methods=['GET', 'POST'])
def register_user():
    """Show and handle submission of form to register user"""

    form = RegisterForm()

    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        is_unique_username = User.query.get(username) is None
        is_unique_email = User.query.filter(User.email == email).one_or_none() is None

        if all([is_unique_username, is_unique_email]):
            new_user = User.register(
                username = username,
                password = form.password.data,
                email = email,
                first_name = form.first_name.data,
                last_name = form.last_name.data
            )

            db.session.add(new_user)
            db.session.commit()

            session[SESSION_USER_KEY] = new_user.username

            return redirect(f'/users/{new_user.username}')

        if not is_unique_username:
            form.username.errors = ['Username already taken']
        if not is_unique_email:
            form.email.errors = ['Email already taken']

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
            session[SESSION_USER_KEY] = user.username
            return redirect(f'/users/{user.username}')
        else:
            form.username.errors = ['Bad name/password']

    return render_template('login.html', form=form)

@app.get('/users/<username>')
def show_user_profile(username):
    """ Render the user profile page only for that individual user """

    if SESSION_USER_KEY not in session or session[SESSION_USER_KEY] != username:
        flash('You must be logged in as the right user to view!')
        return redirect('/')

    return render_template(
        'profile.html',
        user=User.query.get_or_404(username),
        form=CSRFProtectForm())

@app.post('/logout')
def logout_current_user():
    """ Log out the current user by removing their username from the session """

    form = CSRFProtectForm()

    if form.validate_on_submit():
        session.pop(SESSION_USER_KEY, None)
        flash('Successfully logged out!')

    return redirect('/')