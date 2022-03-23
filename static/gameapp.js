const canvas = document.getElementById("drawcanvas");
const socket = io.connect('http://' + document.domain + ':' + location.port); //This creates a socket connection with the flask server
socket.emit("syncSID") //This synchronises the socket id with the server so that the server can contact this user directly.
socket.emit("changeword") //This emits a change word event so that the user can get a word to draw as fast as possible.
const ctx = canvas.getContext("2d");
const todraw = document.getElementById("title");
ctx.canvas.width = 1000;
ctx.canvas.height = 680;
document.getElementById("title").innerHTML = ("Draw: Something"); //Sets the default title to say draw: if the client hasnt yet received a word from the server
const hex = document.getElementById("hex");
const chatinput = document.getElementById("chatinput");

const pos = { x: 0, y: 0 };

function setPosition(e) { //Gets mouse position relative to the canvas position
  const rect = canvas.getBoundingClientRect();
  pos.x = e.clientX - rect.left;
  pos.y = e.clientY - rect.top;
};

document.getElementById("chatinput").addEventListener("keyup", function(event) { //This function lets the user send chat messages by pressing the enter button on their keyboard, without having to pres the send message button with their mouse.
  if (event.key === "Enter") {
    chatsubmit();
  };
});

function chatsubmit() { //This function reads the current text in the chat input field, if its empty the function doesnt run
  if (chatinput.value != ""){ 
    socket.emit('chatsubmit', chatinput.value); //This emits a chatsubmit socket event, along with the message that the user wrote.
    chatinput.value = ''; //This empties the chat input field.
  }
};

socket.on('chatprint', function(message){ //When a message comes in, create a new list element then populate it with the message received
  const node = document.createElement("li"); //Creates a list element
  const textnode = document.createTextNode(message); //Creates a text node and populates it with the message
  node.appendChild(textnode); //adds the text node to the list element
  document.getElementById("chat").appendChild(node); //Adds the list element to the chat, which is an unordered list.
  document.getElementById("chat").scrollTop = document.getElementById("chat").scrollHeight; //Lets the chat box be scrolled properly whenever a message is added to it
});

function draw(e) { //This is the function used to enable drawing on the canvas by the user.
  if (e.buttons !== 1) return; //If the mouse button isnt pressed, the function doesn't run.
  const color = document.getElementById("hex").value; //This gets the value of the hex input field on the drawing page then sets the brush color to the color corresponding to the hex code.
  ctx.beginPath(); //This begins a brush path at the current mouse position.
  const width = document.getElementById("brush").value; //This gets the value of the width input field then sets the brush width to said value.
  ctx.lineWidth = width;
  ctx.lineCap = "round"; //This makes the brush circular
  ctx.strokeStyle = color;
  ctx.moveTo(pos.x, pos.y); //This moves the context variable to the current mouse position relative to the canvas.
  setPosition(e); //This updates the mouse position relative to the canvas.
  ctx.lineTo(pos.x, pos.y); //This makes a line from the position created by beginPath() 
  ctx.stroke(); //This colors in the line created by lineTo()
};

function changeWord() { //This function sends out a changeword socket event, which the server receives, chooses a random word then sends it back to the user with a word changed event
  socket.emit('changeword');
};

socket.on('wordchanged', function(newword){ //This function changes the word that appears on top of the drawer's screen that they have to draw whenever the server sends out a word changed event
  todraw.innerHTML = ("Draw: " + newword)
})

socket.on("refresh", function(){ //This function refreshes the page every time the server sends a refresh message.
  location.reload()
})

colors = { red: '#F00', green: '#0F0', blue: '#00F', yellow: '#FF0', orange: '#F80', purple: '#B0F', lightblue:'#0FF', black: '#000', white: '#FFF' }; //Dictionary of colors used to set the brush color so that a new function doesnt have to be written for each button and its color.

function changecolor(color) { //This function sets the color that the brush will be set to on click of the button given the color of the button.
  hex.value = colors[color];
}

setInterval(function() {   //This function emits a drawing socket message, along with a representation of the current canvas to the server every 0.5 seconds.
  const newUrl = document.getElementById('drawcanvas').toDataURL();
  socket.emit("drawing", newUrl);
}, 250);

setInterval(function() {  //This function emits a syncSID socket message to the server every 30 seconds. This technically isnt 100% necessary as every time a user joins a game or a new round starts, the sids are updated. This is only here as a precaution incase somehow the sids change.
  socket.emit("syncSID");
}, 30000);

document.addEventListener("mouseenter", setPosition); //These event listeners are here so that the drawing works. Every time the cursor enters the area of the canvas, clicks or moves it updates its position.
document.addEventListener("mousedown", setPosition);
document.addEventListener("mousemove", draw);