<template>
    <div class="player-block-container">
        <div class="name-text">
            {{ props.player.NAME }}
        </div>
        <div class="player-years">
        </div>
    </div>
</template>

<script setup>
import { defineProps } from 'vue'

const props = defineProps({
    player: { NAME: String, URL: String, IMGURL: String }
})

const imageLoadError = (e) => {
    console.log('IMAGE FAILED TO LOAD')
    e.target.src = 'https://assets.nhle.com/mugs/nhl/default-skater.png'
}

</script>

<style lang="postcss" scoped>
.player-block-container {
    padding: 10px;
    display: grid;
    grid-template-columns: 1fr;
    grid-template-rows: auto;
    grid-template-areas:
    "name name photo photo"
    ". . photo photo"
    ". . photo photo";
}
.name-text {
    grid-area: name;
}
.player-headshot {
    @apply h-[100px] w-[100px] overflow-hidden;
    grid-area: photo;
}
</style>
