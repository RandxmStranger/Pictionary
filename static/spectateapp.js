const canvas = document.getElementById("spectatecanvas");
const socket = io.connect('http://' + document.domain + ':' + location.port);
const chatinput = document.getElementById("chatinput");
const ctx = canvas.getContext("2d")

let drawing = false;
let uid = null;

function chatsubmit() { //Send the current text in the chat box to the server then clear the chat box
  socket.emit('chatsubmit', chatinput.value);
  chatinput.value = '';
  console.log("message");
}

socket.on("newRound", function(){
  const room = io.sockets.adapter.rooms[socket.room];
  const ids = Object.keys(room.sockets);
  if (room.length == 1) {
    room.drawer = 0;
  }
  else if (socket.id == ids[room.drawer]){
    room.drawer += 1;
    room.drawer %= ids.length;
  }
})

socket.on('chatprint', function(message){ //When a message comes in, create a new list element then populate it with the message received
  const node = document.createElement("li");      
  const textnode = document.createTextNode(message);
  node.appendChild(textnode);
  document.getElementById("chat").appendChild(node);
})

socket.on('drawreceive', function(canvasReceived){
  const receivedImage = new Image(1000,680);
  receivedImage.src = canvasReceived;
  ctx.drawImage(receivedImage, 0, 0);
})

socket.on("NewUID", function(username){
  uid = username
})