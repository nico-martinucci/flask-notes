from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()


def connect_db(app):
    """Connect to database."""

    app.app_context().push()
    db.app = app
    db.init_app(app)


class User(db.Model):
    """Site user table model"""

    __tablename__ = 'users'

    username = db.Column(
        db.String(20),
        primary_key = True
    )
    password = db.Column(
        db.String(100),
        nullable = False
    )
    email = db.Column(
        db.String(50),
        nullable = False,
        unique = True
    )
    first_name = db.Column(
        db.String(30),
        nullable = False
    )
    last_name = db.Column(
        db.String(30),
        nullable = False
    )

    notes = db.relationship('Note', backref='user')

    @property
    def full_name(self):
        """ Returns full name in format 'first_name last_name' """

        return f'{self.first_name} {self.last_name}'

    @classmethod
    def register(cls, username, password, email, first_name, last_name):
        """Register a user with hashed password and return user"""

        hashed = bcrypt.generate_password_hash(password).decode('utf8')

        return cls(
            username = username,
            password = hashed,
            email = email,
            first_name = first_name,
            last_name = last_name
        )

    @classmethod
    def authenticate(cls, username, password):
        """ Authenticate an existing user's username and password """

        user = cls.query.get(username)

        if user and bcrypt.check_password_hash(user.password, password):
            return user

        return False


class Note(db.Model):
    """Note table model"""

    __tablename__ = 'notes'

    id = db.Column(
        db.Integer,
        primary_key = True,
        autoincrement = True
    )
    title = db.Column(
        db.String(100),
        nullable = False
    )
    content = db.Column(
        db.Text,
        nullable = False
    )
    owner = db.Column(
        db.String(20),
        db.ForeignKey('users.username'),
        nullable = False
    )

    @property
    def short_content(self):
        """Return a shortened version of the content"""
        content_split = self.content.split(' ')
        short_content_len = min(len(content_split), 5)
        return ' '.join(content_split[:short_content_len]) + '...'