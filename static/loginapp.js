var socket = io.connect('http://' + document.domain + ':' + location.port);

function join() {
  let room = document.getElementById("rooms").value
  let username = document.getElementById("username").value;
  let data = [room,username]
  socket.emit('join', data)
}