var socket = io.connect('http://' + document.domain + ':' + location.port); //This creates a socket connection with the flask server

function requestforum(){
    socket.emit("requestforumpage")
}

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

socket.on('redirect', function(data) { //This function redirects the user to the address specified by the event, the server will send the request to redirect along with the address to redirect to any time it needs the user to be redirected
    window.location = data.url;
});

socket.on('sendforumpage', function(posts) { 
    let table = document.getElementById("tablebody");

    for(let i=0; i < posts.length; i++) {
        let title = document.createElement("a");
        title.href = "/post/" + posts[i][3];
        let author = document.createElement("p");
        title.innerText = posts[i][0];
        author.innerText = posts[i][2];
        titleheading = document.createElement("h3");
        titleheading.classList.add("display-6");
        titleheading.appendChild(title);
        let titlecell = document.createElement("td");
        titlecell.appendChild(titleheading);
        let authorcell = document.createElement("td");
        authorcell.appendChild(author);
        let tablerow = document.createElement("tr");
        tablerow.appendChild(titlecell);
        tablerow.appendChild(authorcell);
        table.appendChild(tablerow);
    };
});