from flask import Flask, redirect, render_template, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Feedback
from forms import RegisterForm, LoginForm, DeleteForm, FeedbackForm
from werkzeug.exceptions import Unauthorized
import os

app = Flask(__name__)
# uri = os.getenv('DATABASE_URL')
# if uri.startswith('postgres://'):
#     uri = uri.replace('postgres://', "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql:///feedback').replace('postgres://', 'postgresql://')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'hellosecret')
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
debug = DebugToolbarExtension(app)

connect_db(app)
with app.app_context():
    db.drop_all()
    db.create_all()

@app.route('/')
def homepage():
    """Redirect to register."""
    return redirect ('/register')

@app.route('/register', methods=['GET', 'POST'])
def register_user():
    """
    Show a register/create a user form which accept a username, password, email, first_name, last_name.
    Process the registration form by adding a new user. Then redirect to /secret.
    """
    if 'username' in session:
        return redirect(f"/users/{session['username']}")

    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        
        user = User.register(username, password, email, first_name, last_name)
        db.session.add(user)
        db.session.commit()
    
        session['username'] = user.username

        flash (f'User "{user.username}" created.', 'success')
        return redirect (f'/users/{user.username}')
    
    return render_template('register_form.html', form=form)
        
@app.route('/login', methods=['GET', 'POST'])
def login_user():
    """
    Show a form to login user which accept a username and a password.
    Process the login form, ensuring the user is authenticated and going to /secret if so.
    """
    if 'username' in session:
        return redirect(f"/users/{session['username']}")

    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)
        if user:
            flash (f'Welcome back, "{user.username}"!', 'success')
            session['username'] = user.username
            return redirect (f'/users/{user.username}')
        else:
            form.username.errors = ['Invalid username/password!']
    return render_template('login_form.html', form = form)

@app.route('/logout')
def logout_user():
    """
    lear any information from the session and redirect to /
    """
    session.pop('username')
    flash ('Bye bye!', 'success')
    return redirect ('/login')

@app.route('/users/<username>')
def user_info(username):
    if 'username' not in session or username != session['username']:
        raise Unauthorized()

    user = User.query.get(username)
    form = DeleteForm ()

    return render_template('user_info.html', user=user, form=form)

@app.route('/users/<username>/delete', methods=['POST'])
def delete_user(username):
    """
    Remove the user from the database and all of their feedbacks.
    Clear any user information in the session and redirect to /.
    """
    if 'username' not in session or username != session['username']:
        raise Unauthorized()
    
    user = User.query.get(username)
    db.session.delete(user)
    db.session.commit()
    session.pop('username')

    return redirect ('/login')

@app.route('/users/<username>/feedback/add', methods=['GET', 'POST'])
def add_feedback(username):
    """
    Display a form to add feedback. 
    Add a new piece of feedback and redirect to /users/<username>.
    """
    if 'username' not in session or username != session['username']:
        raise Unauthorized()

    form = FeedbackForm()
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        feedback = Feedback(title=title, content=content, username=username)
        db.session.add(feedback)
        flash(f'Feedback "{feedback.title}" created!', 'success')
        db.session.commit()
        return redirect(f'/users/{feedback.username}')
    else:
        return render_template('feedback_form.html', form=form)

@app.route('/feedback/<int:id>/update', methods=['GET', 'POST'])
def update_feedback(id):
    """
    Display a form to edit feedback.
    Update specific piece of feedback and redirect to /users/<username>.
    """
    feedback = Feedback.query.get(id)
    if 'username' not in session or feedback.username != session['username']:
        raise Unauthorized()
    
    form = FeedbackForm(obj=feedback)
    if form.validate_on_submit():
        feedback.title = form.title.data
        feedback.content = form.content.data

        db.session.commit()
        flash(f'Feedback "{feedback.title}" updated!', 'success')
        return redirect (f'/users/{feedback.username}')
    else:
        return render_template('feedback_form.html', form=form, feedback=feedback)

@app.route('/feedback/<int:id>/delete', methods=['POST'])
def delete_feedback(id):
    """Delete a specific piece of feedback and redirect to /users/<username>."""
    feedback = Feedback.query.get(id)

    if 'username' not in session or feedback.username != session['username']:
        raise Unauthorized()
    
    form = DeleteForm()
    if form.validate_on_submit():
        db.session.delete(feedback)
        flash (f'Post "{feedback.title}" deleted.', 'success')
        db.session.commit()

    return redirect (f'/users/{feedback.username}')

    