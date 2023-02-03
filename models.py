"""Models for Feedback app."""

from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from sqlalchemy.schema import DropTable
from sqlalchemy.ext.compiler import compiles

db = SQLAlchemy()
bcrypt = Bcrypt()

def connect_db(app):
    """Connect to database."""
    db.app = app
    db.init_app(app)

@compiles(DropTable, "postgresql")
def _compile_drop_table(element, compiler, **kwargs):
    return compiler.visit_drop_table(element) + " CASCADE"

class User(db.Model):
    """User model."""
    __tablename__ = 'users'
    username = db.Column (db.String(20), primary_key = True, nullable = False, unique = True)
    password = db.Column (db.Text, nullable = False)
    email = db.Column (db.String(50), nullable = False, unique = True)
    first_name = db.Column (db.String(30), nullable = False)
    last_name = db.Column (db.String(30), nullable = False)

    feedback = db.relationship('Feedback', backref = 'user', cascade = "all, delete")

    @classmethod
    def register (cls, username, password, email, first_name, last_name):
        """Register user with hashed password and return user."""
        hashed = bcrypt.generate_password_hash(password)
        hashed_utf8 = hashed.decode('utf8')

        user = cls (username=username, password=hashed_utf8, email=email, first_name=first_name, last_name=last_name)
        db.session.add(user)

        return user
    
    @classmethod
    def authenticate (cls, username, password):
        """Validate that user exists and password is correct.
        Return user if valid; else return False.
        """
        u = User.query.filter_by(username=username).first()
        if u and bcrypt.check_password_hash(u.password, password):
            return u
        else:
            return False

class Feedback(db.Model):
    """Feedback model."""
    __tablename__ = 'feedbacks'
    id = db.Column (db.Integer, primary_key = True, autoincrement = True)
    title = db.Column (db.String(100), nullable = False)
    content = db.Column (db.Text, nullable = False)
    username = db.Column (db.String(20), db.ForeignKey('users.username'), nullable = False)
