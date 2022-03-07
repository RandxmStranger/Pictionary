from flask import Flask, render_template, request, flash, redirect, session
from flask.globals import session
from flask.helpers import url_for
from flask_login.utils import login_required
from flask_socketio import SocketIO, join_room, leave_room
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import random
import json
import time
import re

app = Flask(__name__)
app.config['SECRET_KEY'] = 'HNz898OEWw3qdq8tpkeatPC8GqvExMdw'
app.config['SQLALCHEMY_DATABASE_URI'] ='sqlite:///./database.db'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
socketio = SocketIO(app,async_handlers=True)

sessions = {}
sids = {}

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "/login"

class User(UserMixin, db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key = True) #Creates an id column, which will be used as the primary key for a user to link tables, required to be called id by flask-login
    username = db.Column(db.String(14)) #Creates a username column, usernames cant be more than 14 chars
    password = db.Column(db.String(100))

class Score(db.Model):
    __tablename__ = "score"
    score = db.Column(db.Integer(), primary_key = True)
    user_id = db.Column(db.ForeignKey("user.id"))

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.route("/")
@login_required
def connect():
    user = User.query.filter_by(username=current_user.username).first()
    db.session.commit()
    session['username'] = current_user.username
    return render_template("index.html", username = user.username)

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/register", methods=["POST"])
def register_post():
    username = request.form.get("username")
    password = request.form.get("password")

    if re.fullmatch(" *", password):
        flash("Please enter a password")
        return redirect("/register")
    elif len(password) < 8:
        flash("Your password has to be at least 8 characters long")
        return redirect("/register")
        
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
    for key in sessions:
            if session['username'] in sessions[key].clients:
                for i in sessions[key].clients:
                    socketio.emit('drawreceive', args, room=sids[i])
    

@socketio.on('chatsubmit')
def handle_chat(message):
    for key in sessions:
            if session['username'] in sessions[key].clients:
                goodkey = key
                break
    if message.upper() == sessions[goodkey].word.upper():
        message = (session["username"] +  " Has Guessed The Word. The Word Was: " + sessions[goodkey].word)
        scorerow= Score.query.filter_by(user_id = current_user.id).first()
        scorerow.score += 1
        db.session.commit()
        for i in sessions[goodkey].clients:
            socketio.emit('chatprint', message, room = sids[i])
        time.sleep(3)
        if session['username'] in sessions[goodkey].clients:
            new_round(goodkey)
    else:
        message = session['username'] + ":" + str(message)
        for i in sessions[goodkey].clients:
            print("sending to sid: " , sids[i])
            socketio.emit('chatprint', message, room = sids[i])

@socketio.on('changeword')
def handle_word_change():
    with open("words.json") as f:
        data = json.loads(f.read())
        randomint = random.randint(0,62)
        for key in sessions:
            if session["username"] in sessions[key].clients:
                sessions[key].word = data['words'][randomint]
                break
        socketio.emit('wordchanged', sessions[key].word, room=sids[session["username"]])

class Session():
    def __init__(self, roomcode) -> None:
        self.clients = []
        self.code = roomcode
        self.drawer = 0
        self.started = False
        self.word = "Square"

@socketio.on("newRound")
def new_round(room_code):
    current_room = sessions[room_code]
    if (len(sessions[room_code].clients) == 1):
      current_room.drawer = 0
    else:
      current_room.drawer += 1
      current_room.drawer = current_room.drawer % len(current_room.clients)
      for i in current_room.clients:
        socketio.emit('refresh', room = sids[i])

@socketio.on("join")
def handle_joining(room_code):
    if room_code in sessions:
        join_room(room_code)
        sessions[room_code].clients.append(session['username'])
        sessions[room_code].started = True
        sids[session['username']] = request.sid
        print(request.sid)
        socketio.emit('redirect', {'url': url_for('.gameconnect',r_code=room_code)}, room = sids[session['username']])
    else:
        print("Creating room ", room_code)
        sessions[room_code] = Session(room_code)
        sessions[room_code].clients.append(session['username'])
        join_room(room_code)
        print(request.sid)
        sids[session['username']] = request.sid
        socketio.emit('redirect', {'url': url_for('.gameconnect',r_code=room_code)}, room = sids[session['username']])

@app.route("/game/<r_code>")
@login_required
def gameconnect(r_code):
    print(sessions[r_code].clients[sessions[r_code].drawer])
    print(session['username'])
    if session['username'] == sessions[r_code].clients[sessions[r_code].drawer]:
         return render_template("game.html")
    else:
        return render_template("spectate.html")

@socketio.on("newDrawer")
def handle_joining(room_code):
    join_room(room_code)
    sessions[room_code].clients.append(session['username'])
    sessions[room_code].started = True
    sids[session['username']] = request.sid
    socketio.emit('redirect', {'url': url_for('.gameconnect',r_code=room_code)}, room = sids[session['username']])

@socketio.on("syncSID")
def handle_sids():
    sids[session["username"]] = request.sid

@app.route("/leaderboard")
def handle_leaderboards():
    return render_template("leaderboard.html")

@socketio.on("requestleader")
def send_leader():
    table = db.engine.execute("""
    SELECT score.user_id, user.username, score.score
    FROM user
    INNER JOIN score
    ON user.id = score.user_id
    WHERE score.score IS NOT NULL
    ORDER BY score.score DESC
    """)
    score = []
    for row in table:
        newrow = [row[1],row[2]]
        score.append(newrow)
    print(score)

    socketio.emit("sendleader", score, room = request.sid)

if __name__ == "__main__":
    socketio.run(app, debug = True)