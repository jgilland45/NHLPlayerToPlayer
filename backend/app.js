// To enable Vue CLI: https://stackoverflow.com/questions/4037939/powershell-says-execution-of-scripts-is-disabled-on-this-system
const Express = require("express")();
const Http = require("http").Server(Express);
const Socketio = require("socket.io")(Http);

var position = {
    x: 200,
    y: 200,
};

Socketio.on("connection", socket => {
    socket.emit("position", position);
});

Http.listen(3000, () => {
    console.log("Listening at :3000...");
});