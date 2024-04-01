<template>
    <div id="main-container">
        <div id="btn-container">
            <button @click="goToDaily">Daily</button>
            <button @click="goToUnlimited">Unlimited</button>
        </div>
    </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

function goToDaily () {
    router.push('single-player/daily')
}

function goToUnlimited () {
    router.push('single-player/unlimited')
}

</script>

<style>
</style>
