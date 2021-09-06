var socket = io.connect('http://' + document.domain + ':' + location.port);

function joinroom(){
    room_code = document.getElementById("room_code").value
    socket.emit('join', room_code);
}

socket.on('redirect', function(data) {
    window.location = data.url;
});