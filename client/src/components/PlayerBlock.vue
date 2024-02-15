<template>
    <div class="player-block-container">
        <div class="name-text">
            {{ props.player.name }}
        </div>
        <div class="player-headshot">
            <img src="https://assets.nhle.com/mugs/nhl/default-skater.png" width="100px"/>
        </div>
    </div>
</template>

<script setup>
import { ref, computed, defineProps, defineEmits } from 'vue'

const props = defineProps({
  player: { name: String, url: String }
})

</script>

<style lang="css" scoped>
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
    grid-area: photo;
}
</style>
