from flask import Flask, render_template
from flask_socketio import SocketIO, join_room, leave_room
import sys

app = Flask(__name__)
app.config['SECRET_KEY'] = 'fortnite'
socketio = SocketIO(app)

@socketio.on('join')
def on_join(data):
    username = data['username']
    room = data['room']
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
    return render_template("spectate.html")

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
    print(("message:" + str(message)), file=sys.stdout, flush=True)
    socketio.emit('chatprint', message)

if __name__ == "__main__":
    socketio.run(app, debug = True)