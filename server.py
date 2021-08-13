from flask import Flask, render_template
from flask_socketio import SocketIO, join_room, leave_room
from flask_login import LoginManager, UserMixin
from flask_sqlalchemy import SQLAlchemy
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
    username = db.Column(db.String(15)) #Creates a username column, usernames cant be more than 15 chars
    

@socketio.on('join')
def on_join(data):
    username = data[0]
    room = data[1]
    join_room(room)
    socketio.emit(username + ' has entered the room.', to=room)

@socketio.on('leave')
def on_leave(data):
    username = data['username']
    room = data['room']
    leave_room(room)
    socketio.emit(username + ' has left the room.', to=room)


@app.route("/")
def connect():
    return render_template("login.html")

@app.route("/draw")
def drawconnect():
    return render_template("draw.html")

@app.route("/spectate")
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