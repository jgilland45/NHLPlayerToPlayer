<template>
    <div id="main-container">
        <p>Welcome to NHL Player to Player! Which mode would you like to play?</p>
        <div id="btn-container">
            <button @click="goToSinglePlayer">Single player</button>
            <button>Online battles</button>
        </div>
    </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

function goToSinglePlayer () {
  router.push('single-player')
}

</script>

<style>
</style>
