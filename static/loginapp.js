var socket = io.connect('http://' + document.domain + ':' + location.port);

function goToRegister(){
    location.href = "/register";
}