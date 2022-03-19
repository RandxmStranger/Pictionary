var socket = io.connect('http://' + document.domain + ':' + location.port);//This creates a socket connection with the flask server

function goToRegister(){ //This function takes the user to the register route when they press the login button
    location.href = "/register";
}