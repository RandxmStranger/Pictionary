var socket = io.connect('http://' + document.domain + ':' + location.port); //This creates a socket connection with the flask server

function goToLogin(){ //This function takes the user to the login route when they press the login button.
    location.href = "/login";
}