
from flask import Flask, render_template
from flask_socketio import SocketIO

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

@app.route("/")
def connect():
    return render_template("page.html")

@socketio.on('drawing')
def handle_drawing(path,color,width):
    print("received path", path, color, width)

@socketio.on('chatsubmit')
def handle_chat(message):
    print(("message: ", str(message)))

if __name__ == "__main__":
    socketio.run(app)

