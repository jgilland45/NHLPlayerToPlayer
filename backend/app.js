// To enable Vue CLI: https://stackoverflow.com/questions/4037939/powershell-says-execution-of-scripts-is-disabled-on-this-system
// Lots of good help from https://www.youtube.com/watch?v=HXquxWtE5vA&list=WL&index=31&t=1885s&ab_channel=ChrisCourses
const { dir } = require("console");
const express = require("express");
const http = require("http");
const { Server } = require("socket.io")

const app = express();
const server = http.createServer(app)
const io = new Server(server, {
    cors: {
        origin: "http://localhost:8080",
        methods: ["GET", "POST"],
    },
    pingInterval: 2000,
    pingTimeout: 5000
})

const players = {}

io.on("connection", socket => {
    console.log('a new player connected')
    players[socket.id] = {
        x: Math.floor(Math.random() * 640),
        y: Math.floor(Math.random() * 480)
    }

    io.emit('updatePlayers', players)

    socket.on('disconnect', (reason) => {
        console.log(reason)
        delete players[socket.id]
        io.emit('updatePlayers', players)
    })

    socket.on('move', (direction) => {
        switch (direction) {
            case 'up':
                players[socket.id].y -= 5
                break
            case 'down':
                players[socket.id].y += 5
                break
            case 'left':
                players[socket.id].x -= 5
                break
            case 'right':
                players[socket.id].x += 5
                break
        }
    })

    console.log(players)
});

setInterval(() => {
    io.emit('updatePlayers', players)
}, 15)

server.listen(3001, () => {
    console.log("Listening at :3001...");
});