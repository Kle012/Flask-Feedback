from app import app
from models import db


with app.app_context():
    db.drop_all()
    db.create_all()

app_context = app.app_context()
app_context.push()
