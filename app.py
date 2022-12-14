"""Flask Notes app"""

from flask import Flask, redirect, render_template, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User, Note
from forms import RegisterForm, LoginForm, CSRFProtectForm, NoteForm

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///flask_notes"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "shhh"

connect_db(app)
db.create_all()

toolbar = DebugToolbarExtension(app)

SESSION_USER_KEY = 'user_username'

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

            flash('User successfully created!')
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
            flash('Login successful!')
            return redirect(f'/users/{user.username}')
        else:
            form.username.errors = ['Bad name/password']

    return render_template('login.html', form=form)

@app.get('/users/<username>')
def show_user_profile(username):
    """ Render the user profile page only for that individual user """

    if not check_logged_user(username):
        flash('You must be logged in as the right user to view!')
        return redirect('/')

    return render_template(
        'profile.html',
        user=User.query.get_or_404(username),
        form=CSRFProtectForm()
    )

@app.post('/logout')
def logout_current_user():
    """ Log out the current user by removing their username from the session """

    form = CSRFProtectForm()

    if form.validate_on_submit():
        session.pop(SESSION_USER_KEY, None)
        flash('Successfully logged out!')

    return redirect('/')

@app.post('/users/<username>/delete')
def delete_user(username):
    """ Delete current user and all of their notes! """

    form = CSRFProtectForm()

    if form.validate_on_submit():
        user = User.query.get_or_404(username)
        notes = user.notes

        for note in notes:
            db.session.delete(note)

        db.session.commit()

        db.session.delete(user)
        db.session.commit()

        session.pop(SESSION_USER_KEY, None)
        flash('User successfully deleted!')

    return redirect('/')

@app.route('/users/<username>/notes/add', methods=['GET', 'POST'])
def add_new_note(username):
    """ Show form for and handle adding new notes for the current user """

    if not check_logged_user(username):
        flash('You must be logged in as the right user to view!')
        return redirect('/')

    form = NoteForm()

    if form.validate_on_submit():
        new_note = Note(
            title = form.title.data,
            content = form.content.data,
            owner = username
        )

        db.session.add(new_note)
        db.session.commit()

        flash('Successfully added note!')
        return redirect(f'/users/{username}')

    else:
        return render_template('add_note.html', form=form)

@app.route('/notes/<note_id>/update', methods=['GET', 'POST'])
def update_note(note_id):
    """ Show form for and handle updating notes """

    note = Note.query.get_or_404(note_id)
    username = note.user.username

    if not check_logged_user(username):
        flash('You must be logged in as the right user to view!')
        return redirect('/')

    form = NoteForm(obj = note)

    if form.validate_on_submit():
        note.title = form.title.data
        note.content = form.content.data

        db.session.add(note)
        db.session.commit()

        flash('Successfully updated note!')
        return redirect(f'/users/{username}')
    else:
        return render_template('update_note.html', form=form)

@app.post('/notes/<note_id>/delete')
def delete_note(note_id):
    """ Delete the note matching the provided note_id """

    form = CSRFProtectForm()
    note = Note.query.get_or_404(note_id)
    username = note.user.username

    if form.validate_on_submit():

        db.session.delete(note)
        db.session.commit()

        flash('Note successfully deleted!')

    return redirect(f'/users/{username}')



def check_logged_user(username):
    """ Returns True if the passed username
    matches the username in the session """

    return (SESSION_USER_KEY in session and
        session[SESSION_USER_KEY] == username)
