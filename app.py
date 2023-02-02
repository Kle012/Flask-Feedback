from flask import Flask, redirect, render_template, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User
from forms import RegisterForm, LoginForm

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///feedback'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = "Secret"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
debug = DebugToolbarExtension(app)

connect_db(app)
with app.app_context():
    db.drop_all()
    db.create_all()

@app.route('/')
def homepage():
    """Redirect to register""" 
    return redirect ('/register')

@app.route('/register', methods=['GET', 'POST'])
def register_user():
    """
    Show a register/create a user form which accept a username, password, email, first_name, last_name.
    Process the registration form by adding a new user. Then redirect to /secret.
    """
    form = RegisterForm()
    if form.validate_on_submit():
        data = {k: v for k, v in form.data.items() if k != 'csrf_token'}
        user = User.register(**data)
        db.session.add(user)
        db.session.commit()

        session['username'] = user.username

        flash (f'User {user.username} created.')
        return redirect ('/secret')
    else:
        return render_template('register_form.html', form = form)
        
@app.route('/login', methods=['GET', 'POST'])
def login_user():
    """
    Show a form to login user which accept a username and a password.
    Process the login form, ensuring the user is authenticated and going to /secret if so.
    """
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.authenticate(username, password)
        if user:
            session['username'] = user.username
            return redirect ('/secret')
        else:
            form.username.errors = ['Invalid username/password!']
    return render_template('login_form.html', form = form)

@app.route('/secret')
def secret():
    return render_template('secret.html')