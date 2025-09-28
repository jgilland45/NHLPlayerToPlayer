<template>
    <PlayerCard
        :player-name="playerName"
        :player-image-u-r-l="playerImageURL"
    />
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import PlayerCard from './PlayerCard.vue';

const props = defineProps<{
    id: number,
}>();

const playerName = ref("");
const playerImageURL = computed(() => `https://assets.nhle.com/mugs/nhl/latest/${props.id}.png`);

watch(() => props.id, async (newVal: number) => {
    if (!newVal) return;
    const url = `http://127.0.0.1:8000/players/${newVal}`;
    const rawPlayerData = await (await fetch(url)).json();
    playerName.value = rawPlayerData.full_name;
});

</script>
  
<style scoped lang="postcss">

</style>
  