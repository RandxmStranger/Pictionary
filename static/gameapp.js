const canvas = document.getElementById("drawcanvas");
const socket = io.connect('http://' + document.domain + ':' + location.port);
const ctx = canvas.getContext("2d");
const todraw = document.getElementById("title");
ctx.canvas.width = 1000;
ctx.canvas.height = 680;
document.getElementById("title").innerHTML = ("Draw: " + word);
const hex = document.getElementById("hex");
const chatinput = document.getElementById("chatinput");

let drawing = false;
const pos = { x: 0, y: 0 };

let uid = null;

socket.emit('changeword');

function setPosition(e) { //Gets mouse position relative to the canvas
  const rect = canvas.getBoundingClientRect();
  pos.x = e.clientX - rect.left;
  pos.y = e.clientY - rect.top;
};

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
  location.reload();
  socket.emit('newDrawer', room_code);
});

socket.on('chatprint', function(message){ //When a message comes in, create a new list element then populate it with the message received
  console.log("incoming message");
  const node = document.createElement("li");
  const textnode = document.createTextNode(message);
  node.appendChild(textnode);
  document.getElementById("chat").appendChild(node);
  document.getElementById("chat").scrollTop = document.getElementById("chat").scrollHeight;
});

function draw(e) {
  if (e.buttons !== 1) return;
  const color = document.getElementById("hex").value;
  ctx.beginPath();
  const width = document.getElementById("brush").value;
  ctx.lineWidth = width;
  ctx.lineCap = "round";
  ctx.strokeStyle = color;
  ctx.moveTo(pos.x, pos.y);
  setPosition(e);
  ctx.lineTo(pos.x, pos.y);
  ctx.stroke();
};

function changeWord() {
  socket.emit('changeword');
};

socket.on('wordchanged', function(newword){
  todraw.innerHTML = ("Draw: " + newword);
})

socket.on("refresh", function(){
  location.reload()
})

colors = { red: '#F00', green: '#0F0', blue: '#00F', yellow: '#FF0', orange: '#F80', purple: '#B0F', black: '#000', gray: '#333', gray2: '#666', white: '#FFF' };

function changecolor(color) {
  hex.value = colors[color];
}

setInterval(function() {
  const newUrl = document.getElementById('drawcanvas').toDataURL();
  socket.emit("drawing", newUrl);
}, 500);

document.addEventListener("mouseenter", setPosition);
document.addEventListener("mousedown", setPosition);
document.addEventListener("mousemove", draw);