<template>
    <div class="player-block-container">
        <div class="name-text">
            {{ props.player.NAME }}
        </div>
        <div class="player-headshot">
            <img :src="imgSrc" width="100px"/>
        </div>
    </div>
</template>

<script setup>
import { ref, watch, computed, defineProps, defineEmits } from 'vue'
import { getHeadshotFromUrl } from '@/composables/usePlayerImg'

const props = defineProps({
    player: { NAME: String, URL: String, IMGURL: String }
})

const { newPlayerImgUrL } = getHeadshotFromUrl(props.player)

const imgSrc = computed(() => props.player ? props.player.IMGURL : '')

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
    grid-area: photo;
}
</style>
