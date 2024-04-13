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

const backendPlayers = {}
const SPEED = 10

io.on("connection", socket => {
    console.log('a new player connected')
    backendPlayers[socket.id] = {
        x: Math.floor(Math.random() * 640),
        y: Math.floor(Math.random() * 480),
        sequenceNumber: 0,
    }

    io.emit('updatePlayers', backendPlayers)

    socket.on('disconnect', (reason) => {
        console.log(reason)
        delete backendPlayers[socket.id]
        io.emit('updatePlayers', backendPlayers)
    })

    socket.on('move', ({ direction, sequenceNumber }) => {
        backendPlayers[socket.id].sequenceNumber = sequenceNumber
        switch (direction) {
            case 'up':
                backendPlayers[socket.id].y -= SPEED
                break
            case 'down':
                backendPlayers[socket.id].y += SPEED
                break
            case 'left':
                backendPlayers[socket.id].x -= SPEED
                break
            case 'right':
                backendPlayers[socket.id].x += SPEED
                break
        }
    })

    console.log(backendPlayers)
});

setInterval(() => {
    io.emit('updatePlayers', backendPlayers)
}, 15)

server.listen(3001, () => {
    console.log("Listening at :3001...");
});