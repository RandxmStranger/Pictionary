var socket = io.connect('http://' + document.domain + ':' + location.port);

function joinroom(){
    room_code = document.getElementById("room_code").value
    socket.emit('join', room_code);
}

document.getElementById("room_code").addEventListener("keyup", function(event) {
    if (event.key === "Enter") {
        joinroom();
    };
});

function logout(){
    location.href = "/logout"
}

socket.on('redirect', function(data) {
    window.location = data.url;
});

function leaderboard(){
    location.href = "/leaderboard"
}