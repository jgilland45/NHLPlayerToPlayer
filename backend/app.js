// To enable Vue CLI: https://stackoverflow.com/questions/4037939/powershell-says-execution-of-scripts-is-disabled-on-this-system
const Express = require("express");
var app = Express();
const Http = require("http").Server(app);
const Socketio = require("socket.io")(Http, {
    cors: {
        origin: "http://localhost:8080",
        methods: ["GET", "POST"],
    }
});

var position = {
    x: 200,
    y: 200,
};

Socketio.on("connection", socket => {
    socket.emit("position", position);
    socket.on("move", data => {
        switch (data) {
            case "left":
                position.x -= 5;
                Socketio.emit("position", position);
                break;
            case "right":
                position.x += 5;
                Socketio.emit("position", position);
                break;
            case "up":
                position.y -= 5;
                Socketio.emit("position", position);
                break;
            case "down":
                position.y += 5;
                Socketio.emit("position", position);
                break;
        }
    });
});

Http.listen(3000, () => {
    console.log("Listening at :3000...");
});