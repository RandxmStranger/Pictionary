from flask import Flask, render_template, request, flash, redirect, session
from flask.globals import session
from flask.helpers import url_for
from flask_login.utils import login_required
from flask_socketio import SocketIO, join_room
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    login_required,
    current_user,
    logout_user,
)
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import random
import json
import time
import re

db = SQLAlchemy()
app = Flask(__name__)
app.config["SECRET_KEY"] = "HNz898OEWw3qdq8tpkeatPC8GqvExMdw"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///./database.db"
app.config[
    "SEND_FILE_MAX_AGE_DEFAULT"
] = 0  # This line makes the browser not cache any files, which is very useful for testing and also going to be kept like this as it allows for very easy deployment of any updates to the website.
socketio = SocketIO(app, async_handlers=True)
db.init_app(app)

sessions = (
    {}
)  # A dictionary of sessions, so that each room is easily accessible by its room code
sids = (
    {}
)  # A dictionary of session ids, so that each user's session id is easily accessible with their username.

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "/login"


class User(
    UserMixin, db.Model
):  # This class is an sqlalechemy class, which creates the User SQL table. UserMixin is a flask_login object that lets the user table be used to login users.
    __tablename__ = "user"  # This sets the name of the table to user
    id = db.Column(
        db.Integer, primary_key=True
    )  # The primary key for a user. This variable has to be called id for flask-login to work properly
    username = db.Column(
        db.String(14)
    )  # The username of a user. This cannot be longer than 14 characters for storage space purposes.
    password = db.Column(
        db.String(100)
    )  # A user's password. This is going to be encrypted with sha256 for security.
    score = db.Column(
        db.Integer
    )  # This will be the total score that the user has acquired over their account lifetime.
    games = db.relationship(
        "LinkingTable", back_populates="user"
    )  # This creates a relationship object between the user and the linking table, which will be used to create a many to many relationship between games and users.


class Game(
    db.Model
):  # This class is an SQLAlchemy class, which creates an SQL table called Game.
    __tablename__ = "game"  # This line just sets the name of the table
    game_id = db.Column(
        db.Integer(), primary_key=True, unique=True
    )  # This is the primary key of the table, every game will have an integer id used to identify it in the database.
    game_code = db.Column(
        db.String
    )  # This game code will be the room code that users use to connect to the room. Storing it with the game id makes it easy to query the databse with the room code.
    users = db.relationship(
        "LinkingTable", back_populates="game"
    )  # This creates a relationship object to the linking table, which then links the game to the users in a many to many relationship.


class LinkingTable(
    db.Model
):  # This is an SQLAlchemy class that creates an SQL table called Linking Table.
    __tablename__ = "link"  # This sets the name of the table to "link"
    link_id = db.Column(
        db.Integer(), primary_key=True, unique=True
    )  # This is the primary key of the table, every link between game and user will have na integer id to make it easy to identify.
    game_id = db.Column(
        db.Integer(), db.ForeignKey("game.game_id")
    )  # This foreign key will match a game id in the game table, and will be used along with the user id to create a many to many link between the user and the game.
    user_id = db.Column(
        db.Integer(), db.ForeignKey("user.id")
    )  # This foreign key will match a user id in the user table, and will be used along with the game id to create a many to many relationship between user and game
    score = db.Column(
        db.Integer()
    )  # This stores a users score for the specifiedd game. This is different to the score that is stored in the User table, which is a total of all the score that user has gotten.
    user = db.relationship(
        "User", back_populates="games"
    )  # This creates a relationship between the link table and user table, back_poulates tells the database that the relationship will be used to link the user to a game.
    game = db.relationship(
        "Game", back_populates="users"
    )  # This createsa  relationship between the link table and game table, the back_populates parameter tells the database that the game will be linked to a user.


db.create_all(app=app)  # This line creates the database, using the Flask app object.


@login_manager.user_loader  # This is the user loader, flask-login uses this to find the correct user to login when login is called.
def load_user(id):
    return User.query.get(
        int(id)
    )  # This queries the user database by id, then returns the user with that id.


@app.route("/")  # This is the default route that users are taken to.
@login_required  # This makes it so this page is inaccessible unless a user is logged in with flask-login.
def connect():
    user = User.query.filter_by(
        username=current_user.username
    ).first()  # The user database is queried using the current username, then the user with that username is returned to this variable.
    db.session.commit()  # This saves all the pending changes to the SQL database.
    session[
        "username"
    ] = (
        current_user.username
    )  # The session object is a cookie that stores various data about the user and can be easily accessed by the server. Here, the username is stored in the session cookie.
    return render_template(
        "index.html", username=user.username
    )  # This sends the client the index html page, with the username. The username is added to the page with jinja.


@app.route(
    "/register"
)  # This is the route that users are taken to to register a new account.
def register():
    return render_template(
        "register.html"
    )  # This send the user the register html page.


@app.route(
    "/register", methods=["POST"]
)  # This is the registration route, that takes in the username and password from a html form as a POST body.
def register_post():
    username = request.form.get(
        "username"
    )  # Makes the username from the form into a variable
    password = request.form.get(
        "password"
    )  # Makes the password from the form into a variable

    if re.fullmatch(
        " *", password
    ):  # This is regex to make sure the password isnt empty. The " *" means that if the password is made up of any number of spaces, it will be rejected.
        flash(
            "Please enter a password"
        )  # Flash lets you run code in html using jinja, this runs the code on the register.html page and passes the message "please enter a password".
        return redirect("/register")
    elif (
        len(password) < 8
    ):  # This makes sure that the password the user enters is at least 8 characters long.
        flash(
            "Your password has to be at least 8 characters long"
        )  # Flashes the message if the password is less than 8 characters
        return redirect("/register")

    user = User.query.filter_by(
        username=username
    ).first()  # If all of the password checks are completed, this queries the sql user database to check if a user with that username already exists.

    if (
        user
    ):  # If the query returns a user, this code is run to let the user know the username is taken.
        flash("That Username Is Taken")
        return redirect("/register")

    new_user = User(
        username=username,
        password=generate_password_hash(password, method=("sha256")),
        score=0,
    )  # This creates a new user object, with the entered username and the password encrypted with sha256. It also adds a score to the user and sets it to 0.
    db.session.add(
        new_user
    )  # This makes a new entry in the user table using the new_user object to populate it.
    db.session.commit()  # This commits the sql session.

    return redirect(
        "/login"
    )  # Once a user has finished logging in, they are redirected to the login page to login.


@app.route(
    "/login"
)  # This is the route that users are taken to to login, and whenever they access a page that needs to have a user logged in to be accessed.
def login():
    return render_template("login.html")  # Sends the login page to the user.


@app.route(
    "/login", methods=["POST"]
)  # This is the login route, that takes in the username and password from a html form as a POST body.
def login_post():
    username = request.form.get(
        "username"
    )  # Makes the username from the form into a variable
    password = request.form.get(
        "password"
    )  # Makes the password from the form into a variable

    user = User.query.filter_by(
        username=username
    ).first()  # This queries the user table to see if a user with the same username as the one entered exists.

    if not user or not check_password_hash(
        user.password, password
    ):  # This checks if the user with the username exists, and if it does it checks the password entered with the one saved in the database using sha256
        flash(
            "Your username/password is incorrect"
        )  # If the login is unsuccessful, this message is flashed onto the screen to let the user know that their username/ password is incorrect.
        return redirect("/login")  # This redirects the user back to the login page.

    session[
        "id"
    ] = (
        user.id
    )  # This saves the user's id in the session cookie for easy access by the server
    login_user(
        user
    )  # Once everything else is done flask-login logs in the user with the user object from sqlalchemy

    return redirect("/")  # The user is then redirected to the index page.


@app.route(
    "/logout"
)  # When the user presses the logout button or types the address into the address bar, this code is run.
@login_required  # The user needs to be logged in in order to log out
def logout():
    logout_user()  # This is a flask-login method to logout the currently logged in user.
    return redirect(
        "/login"
    )  # After the user is logged out, they are taken to the login page.


@socketio.on(
    "drawing"
)  # This runs whenever the server receives a drawing event, which the artist sends every 0.5 seconds.
def handle_drawing(args):
    for key in sessions:  # This runs through all of the sessions
        if (
            session["username"] in sessions[key].clients
        ):  # If the person who sent the drawing is in the current session this activates
            for i in sessions[
                key
            ].clients:  # This runs through every client in the session
                socketio.emit(
                    "drawreceive", args, room=sids[i]
                )  # This then sends every client in the session the drawing that was sent to the server
        break  # This stops the sessions being iterated once the correct one has been found


@socketio.on("chatsubmit")  # This runs whenever a user sends a chat message
def handle_chat(message):
    for key in sessions:  # This iterates through all of the sessions
        if (
            session["username"] in sessions[key].clients
        ):  # If the user who sent the message is in the current session, it saves the room key of the current session then breaks the loop so as to not keep iterating through the sessions needlessly
            goodkey = key
            break
    if (
        message.upper() == sessions[goodkey].word.upper()
    ):  # This checks if the message that has been sent is the word that is the current word that is meant to be guessed.
        message = (
            session["username"]
            + " Has Guessed The Word. The Word Was: "
            + sessions[goodkey].word
        )  # If this is the case, a chat message is sent telling the other players who guessed the word and what it was.
        userrow = (
            db.session.query(User).filter_by(id=session["id"]).first()
        )  # The user table is queried using the user id, then the row corresponding to the current user is returned to the variable.
        userrow.score += 1  # The user's score is incremented by one
        gamerow = (
            db.session.query(Game).filter_by(game_code=goodkey).first()
        )  # The game table is queried using the game code, then the row corresponding to the room with that room code is returned to the variable. This will allow the game id to be read from the variable.
        assocrow = (
            db.session.query(LinkingTable)
            .filter_by(user_id=session["id"], game_id=gamerow.game_id)
            .first()
        )  # This queries the LinkingTable table by the user id and game id, then returns the link between the game and the user to the variable. This lets the user's game score be incremented.
        assocrow.score += 1  # The user's game score is incremented by one
        db.session.commit()  # The changes are then commited to the database
        for i in sessions[
            goodkey
        ].clients:  # This iterates through all the users in the current session
            socketio.emit(
                "chatprint", message, room=sids[i]
            )  # This sends the chat message to every user in the session
        time.sleep(
            3
        )  # The program waits for 3 seconds before starting a new round in order to let everyone realise that the word was guessed, and to let them prepare for a the next round
        if session["username"] in sessions[goodkey].clients:
            new_round(
                goodkey
            )  # Starts a new round in the room specified by the good key.
    else:
        message = (
            session["username"] + ":" + str(message)
        )  # If the message wasnt a correct guess, the message becomes the user's who sent the message username, followed by a colon then their message.
        for i in sessions[
            goodkey
        ].clients:  # Iterates through all the clients in the current session
            socketio.emit(
                "chatprint", message, room=sids[i]
            )  # Sends the message to all the clients in the current session


@socketio.on(
    "changeword"
)  # This runs whenever a user pressed the new word button, which sends a "changeword" event.
def handle_word_change():
    with open("words.json") as f:  # This opens the json file of all the possible words.
        data = json.loads(
            f.read()
        )  # This reads the json file and puts its contents into the data variable
        randomint = random.randint(
            0, 66
        )  # This picks a random number between 0 and 62 (the number of words in the json), which will be used to decide which word to use
        for key in sessions:  # This iterates through all the sessions
            if (
                session["username"] in sessions[key].clients
            ):  # If the user who requested the word change is in the current session, the word becomes a random word chosen from the data variable.
                sessions[key].word = data["words"][randomint]
                break  # This breaks the loop so as to not needlessly iterate through all the sessions
        socketio.emit(
            "wordchanged", sessions[key].word, room=sids[session["username"]]
        )  # This emits the new word to the user who requested it, which upon being received will be displayed at the top of their screen.


class Session:  # This is a session (also known as a room) class, it stores a list of clients, the code for the room, the index of the current drawer, wether the game has started, and the current word.
    def __init__(self, roomcode) -> None:
        self.clients = []
        self.code = roomcode
        self.drawer = 0
        self.started = False
        self.word = "Square"


@socketio.on(
    "newRound"
)  # This is called whenever a word is guessed or when a game starts
def new_round(
    room_code,
):  # The room code decides which room the new round is started in
    current_room = sessions[
        room_code
    ]  # This just makes the room code easily accessible with a variable
    if (
        len(sessions[room_code].clients) == 1
    ):  # If theres only one person in the room, then they become the drawer.
        current_room.drawer = 0
    else:
        current_room.drawer += 1  # Increment the drawer index by one.
        current_room.drawer = current_room.drawer % len(
            current_room.clients
        )  # This mods the drawer index with the amount of people in the room, so that the index cycles through each of the clients without going out of range.
        for i in current_room.clients:
            socketio.emit(
                "refresh", room=sids[i]
            )  # Sends a refresh socket event to each user in the room so that their pages are refreshed and they get the correct gui for their role (drawer/spectator)


@socketio.on("join")  # This runs whenever someone joins a room
def handle_joining(room_code):
    if room_code in sessions:  # If the room already exists, the following code runs
        join_room(room_code)  # Adds the user to the socketio room
        gamerow = (
            db.session.query(Game).filter_by(game_code=room_code).first()
        )  # When a user joins a room, the Game table is queried using the room code to find the room row with that room code.
        newassoc = LinkingTable(
            user_id=session["id"], score=0, game_id=gamerow.game_id
        )  # This creates a new entry in the linking table, with the current user id, the current game id and the users score, which is currently 0.
        db.session.add(newassoc)  # This adds the new entry to the database
        db.session.commit()  # This commits the pending changes to the database.
        sessions[room_code].clients.append(
            session["username"]
        )  # Adds the user to the clients list of the session
        sessions[room_code].started = True  # Marks the session as started
        sids[
            session["username"]
        ] = (
            request.sid
        )  # This saves the user's session id in the sids dictionary so its easy to find the sid using the username
        socketio.emit(
            "redirect",
            {"url": url_for(".gameconnect", r_code=room_code)},
            room=sids[session["username"]],
        )  # Redirects the user to the url for their current game
    else:
        print(
            "Creating room ", room_code
        )  # If the room doesnt already exist, it creates a new room
        newgamerow = Game(
            game_code=room_code
        )  # This creates a new entry in the Game table with the room code specified by the user.
        db.session.add(newgamerow)  # This adds the new game entry to the database.
        db.session.commit()  # This commits all the pending changes to the database.
        gamerow = (
            db.session.query(Game).filter_by(game_code=room_code).first()
        )  # This queries the game table with the room code to find the game id.
        newassoc = LinkingTable(
            user_id=session["id"], score=0, game_id=gamerow.game_id
        )  # This creates a new entry in the linking table with the game id and user id, as well as a score for the game, which is set to 0.
        db.session.add(newassoc)  # This adds the entry to the database
        db.session.commit()  # This commits all pending changes to the database.
        sessions[room_code] = Session(
            room_code
        )  # Create a new session and add it to the sessions dictionary so its easily accessible with its room code
        sessions[room_code].clients.append(
            session["username"]
        )  # Adds the current user to the new room's clients list
        join_room(room_code)  # Adds the user to the socketio room
        sids[
            session["username"]
        ] = (
            request.sid
        )  # This saves the user's session id in the sids dictionary so its easy to find the sid using the username
        socketio.emit(
            "redirect",
            {"url": url_for(".gameconnect", r_code=room_code)},
            room=sids[session["username"]],
        )  # Redirects the user to the url for their current game


@app.route(
    "/game/<r_code>"
)  # The route for games, <r_code> makes it so that any room code can be used and it will still lead to this route
@login_required  # You need to be logged in to be in a game room
def gameconnect(r_code):
    if (
        session["username"] == sessions[r_code].clients[sessions[r_code].drawer]
    ):  # If the client is a drawer in the current game, it sends them the game.html
        return render_template("game.html")
    else:
        return render_template(
            "spectate.html"
        )  # If a client is a spectator, it sends them the spectate.html


@socketio.on(
    "syncSID"
)  # Whenever a client emits a syncsid event (Every 30 seconds) this gets run
def handle_sids():
    sids[
        session["username"]
    ] = (
        request.sid
    )  # This saves the user's session id in the sids dictionary for easy access to their sid


@app.route(
    "/leaderboard"
)  # This is the route that users will visit to see the leaderboards, they dont need to be logged in to view it as its not very important.
def handle_leaderboards():
    return render_template("leaderboard.html")


@socketio.on(
    "requestleader"
)  # Whenever a client requests a leaderboard update, this code is run.
def send_leader():  # This SQL queries the User table, and returns all of the usernames and their corresponding scores, in descending order so that the client doesn't have to sort it. This is an example of thin-client computing.
    table = db.engine.execute(
        """ 
    SELECT user.username, user.score
    FROM user
    WHERE user.score IS NOT NULL
    ORDER BY user.score DESC
    """
    )
    score = []
    for row in table:  # This iterate through every row returned by the query
        newrow = [
            row[0],
            row[1],
        ]  # This creates an array with each entry of a username along with their scores so that the score array can be emitted on the socket
        score.append(
            newrow
        )  # This adds the newrow array into the score 2d array so that its ready to be sent by the server

    socketio.emit(
        "sendleader", score, room=request.sid
    )  # This emits the score array to the user who requested it.


@app.route("/forum")
@login_required
def handle_forum():
    return render_template("forum.html", username=session["username"])


@app.route("/newpost", methods=("GET", "POST"))
@login_required
def newpost():
    if request.method == "POST":
        title = request.form["title_input"]
        content = request.form["content_input"]
        if not title:
            flash("Please Include A Title")
        elif not content:
            flash("Please Include Content To Your Post")
        else:
            db.engine.execute(
                "INSERT INTO post (post_title, post_content, post_author) VALUES (:post_title, :post_content, :post_author)",
                post_title=title,
                post_content=content,
                post_author=session["id"],
            )
            return redirect("/forum")
    return render_template("newpost.html")


@socketio.on("requestforumpage")
def send_forumpage():
    poststuple = db.engine.execute(
        """
    SELECT post.post_title, post.post_author, user.username, post.post_id
    FROM post, user
    WHERE user.id = post.post_author
    ORDER BY post.post_id DESC"""
    )
    posts = []
    for i in poststuple:
        posts.append(list(i))
    socketio.emit("sendforumpage", posts, room=request.sid)


"""need to add functionality for deleting, making admin functionality,
adding comments, editing posts etc. """


@app.route("/post/<id>", methods=("GET", "POST"))
@login_required
def viewpost(id):
    if request.method == "POST":
        comment = request.form["comment_input"]
        if not comment:
            flash("Please Include A Title")
        else:
            db.engine.execute(
                "INSERT INTO comment (comment_content, comment_post, comment_author) VALUES (:comment_content, :comment_post, :comment_author)",
                comment_content=comment,
                comment_post=id,
                comment_author=session["id"],
            )
            return redirect("/post/" + str(id))
    else:
        post = db.engine.execute(
            """
            SELECT post.post_title, post.post_content
            FROM post
            WHERE :post_id = post.post_id
            """,
            post_id=id,
        )
        post = list(post)
        return render_template("post.html", title=post[0][0], content=post[0][1])


@socketio.on("requestcomm")
def sendcomments(id):
    print("comments requested")
    commentstuple = db.engine.execute(
        """
            SELECT comment.comment_content, user.username
            FROM comment, user
            WHERE user.id = comment.comment_author AND comment.comment_post = :post_id
            ORDER BY comment.comment_id DESC
            """,
        post_id=id,
    )
    commentslist = []
    for i in commentstuple:
        commentslist.append(list(i))
    socketio.emit("sendcomments", commentslist, room=request.sid)


if __name__ == "__main__":
    socketio.run(
        app, debug=True, host="0.0.0.0", port=5000
    )  # This runs the flask server to enable clients to connect to it.
