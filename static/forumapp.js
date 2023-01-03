var socket = io.connect('http://' + document.domain + ':' + location.port); //This creates a socket connection with the flask server

function makepost(){
    
}

socket.on('redirect', function(data) { //This function redirects the user to the address specified by the event, the server will send the request to redirect along with the address to redirect to any time it needs the user to be redirected
    window.location = data.url;
});