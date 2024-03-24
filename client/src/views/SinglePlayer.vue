<template>
    <div id="main-container">
        <div id="btn-container">
            <button @click="goToDaily">Daily</button>
        </div>
    </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

function goToDaily () {
    router.push('single-player/daily')
}

</script>

<style>
</style>
