var socket = io.connect('http://' + document.domain + ':' + location.port); //This creates a socket connection with the flask server

function new_post(){
    location.href = "/newpost"
}
function game(){ //This function takes the user to the forum route when they press the forum button on the page
    location.href = "/"
}

function leaderboard(){ //This function takes the user to the forum route when they press the forum button on the page
    location.href = "/leaderboard"
}

function logout(){ //This function takes the user to the forum route when they press the forum button on the page
    location.href = "/logout"
}

function requestcomments(){
    let postno = (window.location.href.charAt(window.location.href.length -1))
    console.log(postno)
    socket.emit("requestcomm", postno)
}

socket.on("sendcomments", function(commentslist) { 
    let table = document.getElementById("commentstable");

    for(let i=0; i < commentslist.length; i++) {
        let comment = document.createElement("p");
        let author = document.createElement("p");
        comment.innerText = commentslist[i][0];
        author.innerText = commentslist[i][1];
        let commentcell = document.createElement("td");
        commentcell.appendChild(comment);
        let authorcell = document.createElement("td");
        authorcell.appendChild(author);
        let tablerow = document.createElement("tr");
        tablerow.appendChild(commentcell);
        tablerow.appendChild(authorcell);
        table.appendChild(tablerow);
    };
});