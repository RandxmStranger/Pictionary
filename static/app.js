const canvas = document.getElementById("draw");
var socket = io.connect('http://' + document.domain + ':' + location.port);
const ctx = canvas.getContext("2d");
let word = "Something";
ctx.canvas.width = 1000;
ctx.canvas.height = 700;
document.getElementById("title").innerHTML = ("Draw: " + word);
const hex = document.getElementById("hex");
const chatinput = document.getElementById("chatinput");

var pos = { x: 0, y: 0 };


function setPosition(e) {
  var rect = canvas.getBoundingClientRect();
  pos.x = e.clientX - rect.left;
  pos.y = e.clientY - rect.top;
}

function chatsubmit() {
  socket.emit('chatsubmit', chatinput.value);
  chatinput.value='';
  console.log("message")
}

socket.on( 'connect', function(){
  console.log("connected")
})

socket.on( 'chatprint', function( message){
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
  ctx.lineWidth = document.getElementById("brush").value;
  ctx.lineCap = "round";
  ctx.strokeStyle = color;
  ctx.moveTo(pos.x, pos.y);
  setPosition(e);
  ctx.lineTo(pos.x, pos.y);
  ctx.stroke();
}

function changeWord() {
  word = words[Math.floor(Math.random() * words.length)];
  document.getElementById("title").innerHTML = ("Draw: " + word);
}

async function getWords() {
  const data = await fetch("/words.json").then(res => res.json()).catch(err => console.log(`Error fetching words: ${err}`));
  return data.words;
}

//function setColor(color) {
//  const colors = { red: "#FF0000", green: "#00FF00", blue: "#0000FF", black: "#000000", yellow: "#FFFF00" };
//  if (!colors[color]) return;
//  hex.value = colors[color];
//};

//const buttons = document.querySelectorAll(".colorButton");
//buttons.forEach(button => {
//  button.addEventListener("click", () => setColor(button.value));
//});

function red() {
  hex.value = "#FF0000";
}
function green() {
  hex.value = "#00FF00";
}
function blue() {
  hex.value = "#0000FF";
}
function yellow() {
  hex.value = "#FFFF00";
}
function orange() {
  hex.value = "#FF8800";
}
function purple() {
  hex.value = "#BB00FF";
}
function black() {
  hex.value = "#000000";
}
function gray() {
  hex.value = "#333333";
}
function gray2() {
  hex.value = "#666666";
}
function white() {
  hex.value = "#FFFFFF"
}

document.addEventListener("mouseenter", setPosition);
document.addEventListener("mousedown", setPosition);
document.addEventListener("mousemove", draw);
const words = getWords();