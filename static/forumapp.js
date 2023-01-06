var socket = io.connect('http://' + document.domain + ':' + location.port); //This creates a socket connection with the flask server

function new_post(){
    
}
function game(){ //This function takes the user to the forum route when they press the forum button on the page
    location.href = "/"
}
function leaderboard(){ //This function takes the user to the forum route when they press the forum button on the page
    location.href = "/leaderboard"
}
function logout(){ //This function takes the user to the forum route when they press the forum button on the page
    location.href = "/logout"
}
socket.on('redirect', function(data) { //This function redirects the user to the address specified by the event, the server will send the request to redirect along with the address to redirect to any time it needs the user to be redirected
    window.location = data.url;
});