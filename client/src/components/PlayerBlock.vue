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

const props = defineProps({
    player: { NAME: String, URL: String }
})
const getImgUrl = ref(true)
const imgPartOfUrl = computed(() => props.player.URL ? props.player.URL.slice(11, -5) : '')
const imgSrc = computed(() => {
    if (props.player.URL) {
        return getImgUrl.value !== false ? `https://www.puckdoku.com/faces/${imgPartOfUrl.value}.jpg` : 'https://assets.nhle.com/mugs/nhl/default-skater.png'
    }
    return 'https://assets.nhle.com/mugs/nhl/default-skater.png'
})

watch(imgPartOfUrl, () => {
    if (imgPartOfUrl.value === '') {
        getImgUrl.value = false
    } else {
    // https://stackoverflow.com/questions/18837735/check-if-image-exists-on-server-using-javascript
        const imgURL = `https://www.puckdoku.com/faces/${imgPartOfUrl.value}.jpg`
        const img = new Image()
        img.onload = () => { getImgUrl.value = true }
        img.onerror = () => { getImgUrl.value = false }
        img.src = imgURL
    }
}, { immediate: true })

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
