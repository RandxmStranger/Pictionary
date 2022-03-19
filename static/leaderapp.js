const socket = io.connect('http://' + document.domain + ':' + location.port); //This creates a socket connection with the flask server

socket.on('sendleader', function(scores) { //This function runs whenever the client receives a sendleader event from the server, along with the scores the server sends.
    let leaderboard = document.getElementById("leaderboard"); //This gets the leaderboard div element and puts it into a variable so it's easily accessible
    leaderboard.innerHTML = `<div id="title" class="row epicclassno1">
    <div id="nametitle" class="title epicclassno2 table">Name</div>
    <div id="scoretitle" class="title epicclassno2 table">Score</div>
</div>`; //This html creates a div element which functions as a row in the table, then creates the Name div and Score div inside the row, which both function as titles for the leaderboard columns.

    for(let i=0; i < scores.length; i++) { //This for loop iterates through the received scores until it reaches the last one.
        let name = document.createElement("div"); //This creates a div element that will be used to store the name from the currently iterated row.
        let score = document.createElement("div"); //This creates a div element that will be used to store the score from the currently iterated row.
        name.classList.add("name", "epicclassno2"); //This adds the name and epicclassno2 classes to the div that will hold the username.
        score.classList.add("score", "epicclassno2"); //This adds the score and epicclassno2 classes to the div that will hold the score.
        name.innerText = scores[i][1]; //This takes the username from the currently iterated row in the received scores then puts it into the name div
        score.innerText = scores[i][0]; //This takes the score from the currently iterated row in the received scores then puts it into the score div.
        let scoreRow = document.createElement("div"); //This creates a div that will contain the name div and score div, it will function as a row for the table.
        scoreRow.classList.add("row","epicclassno1"); //This adds the row and epicclassno1 classes to the scoreRow div. This makes it so the row is properly centered
        scoreRow.appendChild(score); //This puts the score div into the scoreRow div
        scoreRow.appendChild(name); //This puts the name div into the scoreRow div
        leaderboard.appendChild(scoreRow); //This puts the scoreRow div into the leaderboard div, which makes it display on the user's screen.
    };
});

function updateLeaderboard(){ //This function is run to request an updated leaderboard from the server.
    socket.emit("requestleader");
};

updateLeaderboard() //This is called to request an updated leaderboard from the server. Without this the user would manually have to press the update leaderboard button to get a leaderboard.