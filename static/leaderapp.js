const socket = io.connect('http://' + document.domain + ':' + location.port);

socket.on('sendleader', function(scores) {
    let leaderboard = document.getElementById("leaderboard");
    leaderboard.innerHTML = `<div id="title" class="row epicclassno1">
    <div id="nametitle" class="title epicclassno2 table">Name</div>
    <div id="scoretitle" class="title epicclassno2 table">Score</div>
</div>`;

    for(let i=0; i < scores.length; i++) {
        let name = document.createElement("div");
        let score = document.createElement("div");
        name.classList.add("name", "epicclassno2");
        score.classList.add("score", "epicclassno2");
        name.innerText = scores[i][1];
        score.innerText = scores[i][0];
        let scoreRow = document.createElement("div");
        scoreRow.classList.add("row","epicclassno1");
        scoreRow.appendChild(score);
        scoreRow.appendChild(name);
        leaderboard.appendChild(scoreRow);
    };
});

function updateLeaderboard(){
    socket.emit("requestleader");
};

updateLeaderboard()