const canvas = document.getElementById("spectatecanvas");
const socket = io.connect('http://' + document.domain + ':' + location.port);
const chatinput = document.getElementById("chatinput");
const ctx = canvas.getContext("2d");

let drawing = false;
let uid = null;
socket.emit("syncSID")

document.getElementById("chatinput").addEventListener("keyup", function(event) {
  if (event.key === "Enter") {
    chatsubmit();
  };
});

function chatsubmit() { //Send the current text in the chat box to the server then clear the chat box
  socket.emit('chatsubmit', chatinput.value);
  chatinput.value = '';
  console.log("message");
};

socket.on('setDrawer', function(room_code) {
  location.reload()
  socket.emit('newDrawer', room_code)
});

socket.on('chatprint', function(message){ //When a message comes in, create a new list element then populate it with the message received
  const node = document.createElement("li");      
  const textnode = document.createTextNode(message);
  node.appendChild(textnode);
  document.getElementById("chat").appendChild(node);
  document.getElementById("chat").scrollTop = document.getElementById("chat").scrollHeight;
});

socket.on("refresh", function(){
  location.reload();
});

setInterval(function() {
  socket.emit("syncSID");
}, 30000);

socket.on('drawreceive', function(canvasReceived){
  const receivedImage = new Image(1000,680);
  receivedImage.src = canvasReceived;
  ctx.drawImage(receivedImage, 0, 0);
});

socket.on("NewUID", function(username){
  uid = username;
});