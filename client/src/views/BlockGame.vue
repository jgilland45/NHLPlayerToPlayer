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
const frontendPlayers = ref({})
const context = ref()
const game = ref()

const playerInputs = ref([])
const sequenceNumber = ref(0)
const SPEED = 10

const drawBlocks = () => {
    context.value.clearRect(0, 0, game.value.width, game.value.height)
    for (const id in frontendPlayers.value) {
        context.value.fillRect(frontendPlayers.value[id].position.x, frontendPlayers.value[id].position.y, 20, 20)
    }
}

socket.value.on('updatePlayers', (backendPlayers) => {
    for (const id in backendPlayers) {
        const backendPlayer = backendPlayers[id]
        if (!frontendPlayers.value[id]) {
            frontendPlayers.value[id] = {
                position: {
                    x: backendPlayer.x,
                    y: backendPlayer.y,
                    randInt: Math.floor(Math.random() * 100)
                }
            }
        } else {
            if (id === socket.value.id) {
            // if a player already exists
                frontendPlayers.value[id].position.x = backendPlayer.x
                frontendPlayers.value[id].position.y = backendPlayer.y
                const lastBackendInputIndex = playerInputs.value.findIndex(input => {
                    return backendPlayer.sequenceNumber === input.sequenceNumber
                })
                if (lastBackendInputIndex > -1) {
                    playerInputs.value.splice(0, lastBackendInputIndex + 1)
                }
                playerInputs.value.forEach(input => {
                    frontendPlayers.value[id].position.x += input.dx
                    frontendPlayers.value[id].position.y += input.dy
                })
            } else {
                // for all other players
                frontendPlayers.value[id].position.x = backendPlayer.x
                frontendPlayers.value[id].position.y = backendPlayer.y
            }
        }
    }

    for (const id in frontendPlayers.value) {
        if (!backendPlayers[id]) {
            delete frontendPlayers.value[id]
        }
    }
    drawBlocks()
})

const move = (direction) => {
    if (!frontendPlayers.value[socket.value.id]) return
    switch (direction) {
    case 'up':
        sequenceNumber.value++
        playerInputs.value.push({ sequenceNumber: sequenceNumber.value, dx: 0, dy: -SPEED })
        frontendPlayers.value[socket.value.id].position.y -= SPEED
        break
    case 'down':
        sequenceNumber.value++
        playerInputs.value.push({ sequenceNumber: sequenceNumber.value, dx: 0, dy: SPEED })
        frontendPlayers.value[socket.value.id].position.y += SPEED
        break
    case 'left':
        sequenceNumber.value++
        playerInputs.value.push({ sequenceNumber: sequenceNumber.value, dx: -SPEED, dy: 0 })
        frontendPlayers.value[socket.value.id].position.x -= SPEED
        break
    case 'right':
        sequenceNumber.value++
        playerInputs.value.push({ sequenceNumber: sequenceNumber.value, dx: SPEED, dy: 0 })
        frontendPlayers.value[socket.value.id].position.x += SPEED
        break
    }
    socket.value.emit('move', { direction: direction, sequenceNumber: sequenceNumber.value })
    drawBlocks()
}

onMounted(() => {
    context.value = game.value.getContext('2d')
})

</script>

<style scoped>
</style>
