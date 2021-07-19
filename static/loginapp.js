var socket = io.connect('http://' + document.domain + ':' + location.port);

function join() {
  socket.emit('join', room, username)
}

