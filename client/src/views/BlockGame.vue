<template>
  <div>
    <canvas
      ref="game"
      width="640"
      height="480"
      style="border: 1px solid black;">
    </canvas>
    <div>
      <button @click="move('right')">Right</button>
      <button @click="move('left')">Left</button>
      <button @click="move('up')">Up</button>
      <button @click="move('down')">Down</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { io } from 'socket.io-client'

const socket = ref(io('http://localhost:3001'))
const players = ref({})
const context = ref()
const game = ref()

const drawBlocks = () => {
    context.value.clearRect(0, 0, game.value.width, game.value.height)
    for (const id in players.value) {
        context.value.fillRect(players.value[id].position.x, players.value[id].position.y, 20, 20)
    }
}

socket.value.on('updatePlayers', (backendPlayers) => {
    for (const id in backendPlayers) {
        const backendPlayer = backendPlayers[id]
        if (!players.value[id]) {
            players.value[id] = {
                position: {
                    x: backendPlayer.x,
                    y: backendPlayer.y,
                    randInt: Math.floor(Math.random() * 100)
                }
            }
        } else {
            // if a player already exists
            players.value[id].position.x = backendPlayer.x
            players.value[id].position.y = backendPlayer.y
        }
    }

    for (const id in players.value) {
        if (!backendPlayers[id]) {
            delete players.value[id]
        }
    }
    drawBlocks()
})

onMounted(() => {
    context.value = game.value.getContext('2d')
})

const move = (direction) => {
    if (!players.value[socket.value.id]) return
    socket.value.emit('move', direction)
}

</script>

<style scoped>
</style>
