const canvas = document.getElementById("drawcanvas");
var socket = io.connect('http://' + document.domain + ':' + location.port);
const ctx = canvas.getContext("2d");
const todraw = document.getElementById("title");
ctx.canvas.width = 1000;
ctx.canvas.height = 680;
document.getElementById("title").innerHTML = ("Draw: " + word);
const hex = document.getElementById("hex");
const chatinput = document.getElementById("chatinput");

drawing = false
var pos = { x: 0, y: 0 };

function setPosition(e) { //Gets mouse position relative to the canvas
  var rect = canvas.getBoundingClientRect();
  pos.x = e.clientX - rect.left;
  pos.y = e.clientY - rect.top;
}

function chatsubmit() { //Send the current text in the chat box to the server then clear the chat box
  socket.emit('chatsubmit', chatinput.value);
  chatinput.value='';
  console.log("message")
}

socket.on("newRound", function(){
  var room = io.sockets.adapter.rooms[socket.room]
  var ids = Object.keys(room.sockets)
  if (room.length == 1) {
    room.drawer = 0
  }
  else if (socket.id == ids[room.drawer]){
    room.drawer += 1
    room.drawer %= ids.length
  }
})

socket.on('chatprint', function(message){ //When a message comes in, create a new list element then populate it with the message received
  console.log("incoming message");
  var node = document.createElement("LI");      
  var textnode = document.createTextNode(message);
  node.appendChild(textnode);
  document.getElementById("chat").appendChild(node);
})

function draw(e) {
  if (e.buttons !== 1) return;
  var color = document.getElementById("hex").value;
  ctx.beginPath();
  var width = document.getElementById("brush").value;
  ctx.lineWidth = width;
  ctx.lineCap = "round";
  ctx.strokeStyle = color;
  ctx.moveTo(pos.x, pos.y);
  setPosition(e);
  ctx.lineTo(pos.x, pos.y);
  ctx.stroke();
  var canvasToSend = document.getElementById('drawcanvas').toDataURL();
  socket.emit('drawing',canvasToSend)
}

function changeWord() {
  socket.emit('changeword')
}

socket.on('wordchanged', function(newword){
  todraw.innerHTML = ("Draw: " + newword);
})

colors = {'red': '#F00', 'green':'#0F0', 'blue':'00F', 'yellow':'#FF0', 'orange':'#F80', 'purple':'#B0F', 'black':'#000', 'gray':'#333', 'gray2':'#666', 'white':'#FFF'}

function changecolor(color) {
  hex.value = colors[color]
}

document.addEventListener("mouseenter", setPosition);
document.addEventListener("mousedown", setPosition);
document.addEventListener("mousemove", draw);