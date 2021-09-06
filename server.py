from flask import Flask, render_template, request, flash, redirect
from flask.globals import current_app, session
from flask.helpers import url_for
from flask_login.utils import _get_user, login_required
from flask_socketio import SocketIO, join_room, leave_room, rooms
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import random
import json

newword = "Something"
app = Flask(__name__)
app.config['SECRET_KEY'] = 'fortnite'
app.config['SQLALCHEMY_DATABASE_URI'] ='sqlite:///C:/Users/Dustin/Pictionary 2.0/login.db'
socketio = SocketIO(app)

sessions = {}
sids = {}

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "/login"

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key = True) #Creates an id column, which will be used as the primary key for a user to link tables, required to be called id by flask-login
    username = db.Column(db.String(14), unique = True) #Creates a username column, usernames cant be more than 14 chars
    password = db.Column(db.String(100))
    #successful_guesses = db.Column(db.Integer)
    #successful_drawings = db.Column(db.Integer)

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.route("/")
@login_required
def connect():
    user = User.query.filter_by(username=current_user.username).first()
    db.session.commit()
    return render_template("index.html", username = user.username)

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

@socketio.on('drawing')
def handle_drawing(args):
    print("received drawing", args)
    socketio.emit('drawreceive', args)

@socketio.on('chatsubmit')
def handle_chat(message,r_code):
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

class Session():
    def __init__(self, roomcode) -> None:
        self.clients = []
        self.code = roomcode
        self.drawer = 0
        self.started = False

@socketio.on("newRound")
def new_round(room_code):
    session = sessions[room_code]
    if (len(session.clients) == 1):
      session.drawer = 0
    else:
      session.drawer += 1
      session.drawer = session.drawer % len(session.clients)
    socketio.emit("setDrawer", room = room_code)

@socketio.on("join")
def handle_joining(room_code):
    if room_code in sessions:
        join_room(room_code)
        sessions[room_code].clients.append(current_user)
        sessions[room_code].started = True
        sids[current_user.username] = request.sid
        socketio.emit('redirect', {'url': url_for('.gameconnect',r_code=room_code)}, room = sids[current_user.username])
    else:
        print("Creating room ", room_code)
        sessions[room_code] = Session(room_code)
        sessions[room_code].clients.append(current_user)
        join_room(room_code)
        sids[current_user.username] = request.sid
        socketio.emit('redirect', {'url': url_for('.gameconnect',r_code=room_code)}, room = sids[current_user.username])

@app.route("/game/<r_code>")
@login_required
def gameconnect(r_code):
    if sessions[r_code].started == False:
         return render_template("game.html")
    else:
        return render_template("spectate.html")

if __name__ == "__main__":
    socketio.run(app, debug = True)