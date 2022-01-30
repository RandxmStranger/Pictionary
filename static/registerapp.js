var socket = io.connect('http://' + document.domain + ':' + location.port);

function goToLogin(){
    location.href = "/login";
}