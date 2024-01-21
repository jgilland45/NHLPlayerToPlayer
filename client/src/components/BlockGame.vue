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

const socket = ref(io('http://localhost:3000'))
const context = ref()
const game = ref()
const position = ref({
  x: 0,
  y: 0
})

onMounted(() => {
  context.value = game.value.getContext('2d')
  socket.value.on('position', data => {
    position.value = data
    context.value.clearRect(0, 0, game.value.width, game.value.height)
    context.value.fillRect(position.value.x, position.value.y, 20, 20)
  })
})

const move = (direction) => {
  socket.value.emit('move', direction)
}

</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
