from flask import Flask, render_template, request, flash, redirect, session
from flask.globals import session
from flask.helpers import url_for
from flask_login.utils import login_required
from flask_socketio import SocketIO, join_room 
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
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0 #This line makes the browser not cache any files, which is very useful for testing and also going to be kept like this as it allows for very easy deployment of any updates to the website.
socketio = SocketIO(app,async_handlers=True)

sessions = {}
sids = {}

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "/login"

class User(UserMixin, db.Model): #This class is an sqlalechemy class, which enables easy use of sql databases without having to write queries. Even though this could be used to create tables, sql was manually executed for table creation.
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key = True) #The primary key for a user. This variable has to be called id for flask-login to work properly
    username = db.Column(db.String(14)) #The username of a user. This cannot be longer than 14 characters for storage space purposes.
    password = db.Column(db.String(100)) #A user's password. This is going to be encrypted with sha256 for security.

class Score(db.Model):
    __tablename__ = "score"
    score = db.Column(db.Integer())
    user_id = db.Column(db.ForeignKey("user.id"), primary_key = True, unique = True)

@login_manager.user_loader #This is the user loader, flask-login uses this to find the correct user to login when login is called.
def load_user(id):
    return User.query.get(int(id)) #This queries the user database by id, then returns the user with that id.

@app.route("/") #This is the default route that users are taken to.
@login_required #This makes it so this page is inaccessible unless a user is logged in with flask-login.
def connect():
    user = User.query.filter_by(username=current_user.username).first() #The user database is queried using the current username, then the user with that username is returned to this variable.
    db.session.commit()
    session['username'] = current_user.username #The session object is a cookie that stores various data about the user and can be easily accessed by the server. Here, the username is stored in the session cookie.
    return render_template("index.html", username = user.username) #This sends the client the index html page, with the username. The username is added to the page with jinja.

@app.route("/register") #This is the route that users are taken to to register a new account.
def register():
    return render_template("register.html") #This send the user the register html page.

@app.route("/register", methods=["POST"]) #This is the registration route, that takes in the username and password from a html form as a POST body.
def register_post():
    username = request.form.get("username") #Makes the username from the form into a variable
    password = request.form.get("password") #Makes the password from the form into a variable

    if re.fullmatch(" *", password):  #This is regex to make sure the password isnt empty. The " *" means that if the password is made up of any number of spaces, it will be rejected.
        flash("Please enter a password") #Flash lets you run code in html using jinja, this runs the code on the register.html page and passes the message "please enter a password".
        return redirect("/register")
    elif len(password) < 8: #This makes sure that the password the user enters is at least 8 characters long.
        flash("Your password has to be at least 8 characters long") #Flashes the message if the password is less than 8 characters
        return redirect("/register")
        
    user = User.query.filter_by(username=username).first() #If all of the password checks are completed, this queries the sql user database to check if a user with that username already exists.

    if user: #If the query returns a user, this code is run to let the user know the username is taken.
        flash("That Username Is Taken")
        return redirect("/register")
    
    new_user = User(username=username, password=generate_password_hash(password, method=("sha256"))) #This creates a new user object, with the entered username and the password encrypted with sha256.
    new_score = Score(score=0) #This creates a new score object that is linked to the user.
    db.session.add(new_user) #This makes a new entry in the user table using the new_user object to populate it.
    db.session.add(new_score) #This makes a new entry in the score table, using the new_score object to populate it.
    db.session.commit() #This commits the sql session.

    return redirect("/login") #Once a user has finished logging in, they are redirected to the login page to login.

@app.route("/login") #This is the route that users are taken to to login, and whenever they access a page that needs to have a user logged in to be accessed.
def login():
    return render_template("login.html") #Sends the login page to the user.

@app.route("/login", methods=["POST"])  #This is the login route, that takes in the username and password from a html form as a POST body.
def login_post():
    username = request.form.get("username") #Makes the username from the form into a variable
    password = request.form.get("password") #Makes the password from the form into a variable

    user = User.query.filter_by(username=username).first() #This queries the user table to see if a user with the same username as the one entered exists.

    if not user or not check_password_hash(user.password, password): #This checks if the user with the username exists, and if it does it checks the password entered with the one saved in the database using sha256
        flash("Your username/password is incorrect") #If the login is unsuccessful, this message is flashed onto the screen to let the user know that their username/ password is incorrect.
        return redirect("/login") #This redirects the user back to the login page.
    
    session["id"] = user.id #This saves the user's id in the session cookie for easy access by the server
    login_user(user) #Once everything else is done flask-login logs in the user with the user object from sqlalchemy

    return redirect("/") #The user is then redirected to the index page.

@app.route("/logout") #When the user presses the logout button or types the address into the address bar, this code is run.
@login_required #The user needs to be logged in in order to log out
def logout():
    logout_user() #This is a flask-login method to logout the currently logged in user.
    return redirect("/login") #After the user is logged out, they are taken to the login page.

@socketio.on('drawing') #This runs whenever the server receives a drawing event, which the artist sends every 0.5 seconds.
def handle_drawing(args):
    for key in sessions: #This runs through all of the sessions
            if session['username'] in sessions[key].clients: #If the person who sent the drawing is in the current session this activates
                for i in sessions[key].clients: #This runs through every client in the session
                    socketio.emit('drawreceive', args, room=sids[i]) #This then sends every client in the session the drawing that was sent to the server
            break #This stops the sessions being iterated once the correct one has been found

@socketio.on('chatsubmit') #This runs whenever a user sends a chat message
def handle_chat(message):
    for key in sessions: #This iterates through all of the sessions 
            if session['username'] in sessions[key].clients: #If the user who sent the message is in the current session, it saves the room key of the current session then breaks the loop so as to not keep iterating through the sessions needlessly
                goodkey = key
                break
    if message.upper() == sessions[goodkey].word.upper(): #This checks if the message that has been sent is the word that is the current word that is meant to be guessed.
        message = (session["username"] +  " Has Guessed The Word. The Word Was: " + sessions[goodkey].word) #If this is the case, a chat message is sent telling the other players who guessed the word and what it was.
        scorerow = db.session.query(Score).filter_by(user_id = session["id"]).first() #The score table is queried using the user id, then the row corresponding to the current user is returned to the variable.
        scorerow.score += 1 #The user's score is incremented by one
        db.session.commit() #The changes are then commited to the database
        for i in sessions[goodkey].clients: #This iterates through all the users in the current session
            socketio.emit('chatprint', message, room = sids[i]) #This sends the chat message to every user in the session
        time.sleep(3) #The program waits for 3 seconds before starting a new round in order to let everyone realise that the word was guessed, and to let them prepare for a the next round
        if session['username'] in sessions[goodkey].clients:
            new_round(goodkey) #Starts a new round in the room specified by the good key.
    else:
        message = session['username'] + ":" + str(message) #If the message wasnt a correct guess, the message becomes the user's who sent the message username, followed by a colon then their message.
        for i in sessions[goodkey].clients: #Iterates through all the clients in the current session
            socketio.emit('chatprint', message, room = sids[i]) #Sends the message to all the clients in the current session

@socketio.on('changeword') #This runs whenever a user pressed the new word button, which sends a "changeword" event.
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
    if session['username'] == sessions[r_code].clients[sessions[r_code].drawer]:
         return render_template("game.html")
    else:
        return render_template("spectate.html")

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

    socketio.emit("sendleader", score, room = request.sid)

if __name__ == "__main__":
    socketio.run(app, debug = True, host="0.0.0.0", port=5000)