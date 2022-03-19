var socket = io.connect('http://' + document.domain + ':' + location.port); //This creates a socket connection with the flask server

function joinroom(){
    room_code = document.getElementById("room_code").value //This function sends a join socket event along with the room code that the user entered to the server
    socket.emit('join', room_code);
}

document.getElementById("room_code").addEventListener("keyup", function(event) { //This function allows the user to press enter to join a room, so that they dont have to press the join room button with their mouse every time.
    if (event.key === "Enter") {
        joinroom();
    };
});

function logout(){ //This function takes the user to the logout route when they press the logout button on the page
    location.href = "/logout"
}

socket.on('redirect', function(data) { //This function redirects the user to the address specified by the event, the server will send the request to redirect along with the address to redirect to any time it needs the user to be redirected
    window.location = data.url;
});

function leaderboard(){ //This function takes the user to the leaderboard route when they press the leaderboard button on the page
    location.href = "/leaderboard"
}