from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy(app)

class User(UserMixin, db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key = True) #Creates an id column, which will be used as the primary key for a user to link tables, required to be called id by flask-login
    username = db.Column(db.String(14)) #Creates a username column, usernames cant be more than 14 chars
    password = db.Column(db.String(100))
