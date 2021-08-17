from flask import Flask, render_template, request, flash, redirect
from flask.globals import current_app, session
from flask.helpers import url_for
from flask_login.utils import login_required
from flask_socketio import SocketIO, join_room, leave_room
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import json
import random

newword = "Something"
app = Flask(__name__)
app.config['SECRET_KEY'] = 'fortnite'
app.config['SQLALCHEMY_DATABASE_URI'] ='sqlite:///C:/Users/Dustin/Pictionary/login.db'
socketio = SocketIO(app)

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key = True) #Creates an id column, which will be used as the primary key for a user to link tables, required to be called id by flask-login
    username = db.Column(db.String(14), unique = True) #Creates a username column, usernames cant be more than 15 chars
    password = db.Column(db.String(100))
    
@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.route("/")
@login_required
def connect():
    return render_template("welcome.html", username = current_user.username)

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/register", methods=["POST"])
def register_post():
    username = request.form.get("username")
    password = request.form.get("password")
    
    user = User.query.filter_by(username=username).first()

    if user:
        flash("That Username Is Taken")
        return redirect("/register")
    
    new_user = User(username=username, password=generate_password_hash(password, method=("sha256")))
    db.session.add(new_user)
    db.session.commit()

    return redirect("/login")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login_post():
    username = request.form.get("username")
    password = request.form.get("password")

    user = User.query.filter_by(username=username).first()

    if not user or not check_password_hash(user.password, password):
        flash("Your username/password is incorrect")
        return redirect("/login")
    
    login_user(user)

    return redirect("/")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/login")

@app.route("/draw")
@login_required
def drawconnect():
    return render_template("draw.html")

@app.route("/spectate")
@login_required
def spectateconnect():
    return render_template("spectate.html")

@socketio.on('drawing')
def handle_drawing(args):
    print("received drawing", args)
    socketio.emit('drawreceive', args)

@socketio.on('chatsubmit')
def handle_chat(message):
    if message.upper() == newword.upper():
        message = "---SOMEONE HAS GUESSED THE WORD---"
    print("message:" + str(message))
    socketio.emit('chatprint', message)

@socketio.on('changeword')
def handle_word_change():
    with open('words.json') as f:
        data = json.loads(f.read())
        randomint = random.randint(0,5)
        global newword
        newword = data['words'][randomint]
        socketio.emit('wordchanged', newword)

if __name__ == "__main__":
    socketio.run(app, debug = True)