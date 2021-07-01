from flask import Flask, render_template
from flask_socketio import SocketIO
import sys

app = Flask(__name__)
app.config['SECRET_KEY'] = 'fortnite'
socketio = SocketIO(app)

@app.route("/")
def connect():
    return render_template("page.html")

@socketio.on('drawing')
def handle_drawing(args):
    print("received drawing", args)
    socketio.emit('drawreceive', args)

@socketio.on('chatsubmit')
def handle_chat(message):
    print((("message:" + str(message))), file=sys.stdout, flush=True)
    socketio.emit('chatprint', message)

if __name__ == "__main__":
    socketio.run(app, debug = True)