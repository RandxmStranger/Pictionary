const canvas = document.getElementById("draw");
var socket = io.connect('http://' + document.domain + ':' + location.port);
const ctx = canvas.getContext("2d");
ctx.canvas.width = 1000;
ctx.canvas.height = 680;
const chatinput = document.getElementById("chatinput");

function chatsubmit() {
  socket.emit('chatsubmit', chatinput.value);
  chatinput.value='';
  console.log("message")
}

socket.on('connect', function(){
  console.log("connected")
  socket.emit('createid')
})

socket.on('chatprint', function(message){
  console.log("incoming message");
  var node = document.createElement("LI");
  var textnode = document.createTextNode(message);
  node.appendChild(textnode);
  document.getElementById("chat").appendChild(node);
})

socket.on('receiveid', function(id){
  const clientid = id
  return clientid
})

socket.on('drawreceive', function(args){
  console.log("Incoming drawing")
  ctx.beginPath();
  ctx.lineWidth = args[5];
  ctx.lineCap = "round";
  ctx.strokeStyle = args[4];
  ctx.moveTo(args[0], args[1]);
  ctx.lineTo(args[2], args[3]);
  ctx.stroke();
})