///const socket = io.connect('http://' + document.domain + ':' + location.port);
///
///socket.on('sendleader', function(score) {
///    console.log("received scores")
///    let leaderboard = document.getElementById("leaderboard");
///    leaderboard.innerHTML = "";
///
///    for(row in score) {
///        console.log(row)
///        let name = document.createElement("div");
///        let score = document.createElement("div");
///        name.classList.add("name");
///        score.classList.add("score");
///        name.innerText = row[1];
///        score.innerText = row[2];
///
///        let scoreRow = document.createElement("div");
///        scoreRow.classList.add("row");
///        scoreRow.appendChild(name);
///        scoreRow.appendChild(score);
///        leaderboard.appendChild(scoreRow);
///  }});
///s
///socket.emit("requestleader")

let scores = [['fortniteman', 69], ['2', 46], ['4', 43], ['1', 32], ['dustin', 7]]

for(let i=0; i < scores.length; i++) {
    console.log(scores[i])
    let name = document.createElement("div");
    let score = document.createElement("div");
    name.classList.add("name");
    score.classList.add("score");
    name.innerText = scores[i][1];
    score.innerText = scores[i][0];

    let scoreRow = document.createElement("div");
    scoreRow.classList.add("row");
    scoreRow.appendChild(name);
    scoreRow.appendChild(score);
    leaderboard.appendChild(scoreRow);
};
