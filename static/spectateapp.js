const canvas = document.getElementById("spectatecanvas");
const socket = io.connect('http://' + document.domain + ':' + location.port); //This creates a socket connection with the flask server
const chatinput = document.getElementById("chatinput");
const ctx = canvas.getContext("2d");
ctx.canvas.width = 1000;
ctx.canvas.height = 680;

socket.emit("syncSID") //This synchronises the socket id with the server so that the server can contact this user directly.

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

socket.on("refresh", function(){ //This function refreshes the page every time the server sends a refresh message.
  location.reload()
});

setInterval(function() { //This function emits a syncSID socket message to the server every 30 seconds. This technically isnt 100% necessary as every time a user joins a game or a new round starts, the sids are updated. This is only here as a precaution incase somehow the sids change.
  socket.emit("syncSID");
}, 30000);

socket.on('drawreceive', function(canvasReceived){ //This function runs whenver the client receives a canvas from the server.
  const receivedImage = new Image(1000,680); //This creates a new Image element with width of 1000 pixels and height 680 pixels.
  receivedImage.src = canvasReceived; //This makes the source of the image element the encoded string received by the client.
  ctx.drawImage(receivedImage, 0, 0); //This draws the received image on the context element of the canvas, the 0,0 means it draws the image starting from the top left corner of the canvas.
});