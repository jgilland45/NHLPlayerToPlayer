<template>
  <div class="players-list">
    <InputSearch v-model="searchTerm" />
    <PlayerCard
      v-for="player in filteredResults"
      v-if="filteredResultsLength <= DISPLAY_LIMIT"
      :player-name="player.item.name"
      :player-image-u-r-l="player.item.image_url"
      @click="onPlayerChoiceClick(player.refIndex)"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, watchEffect, onMounted } from 'vue';
import InputSearch from './InputSearch.vue';
import PlayerCard from './PlayerCard.vue';
import { useFuse } from '@vueuse/integrations/useFuse';

type Player = {
  playerid: number;
  name: string;
  image_url: string;
}

const DISPLAY_LIMIT = 50;

const searchTerm = ref<string>('');
const players = ref<Player[]>([])

const options = computed(() => ({
  fuseOptions: {
    threshold: 0.3,
    keys: ['name'],
  },
}));

const { results: fuseResults, fuse } = useFuse(searchTerm, players, options);
// Filtered results to display
const filteredResults = computed(() => fuseResults.value);
const filteredResultsLength = computed(() => filteredResults.value.length);

const onPlayerChoiceClick = (idx: number) => {
  console.log(players.value[idx]);
};

async function fetchPlayers() {
  try {
    const response = await fetch('http://127.0.0.1:8000/players');
    const data: { players: { playerid: number; name: string }[] } = await response.json();

    players.value = data.players.map(player => ({
      ...player,
      image_url: `https://assets.nhle.com/mugs/nhl/latest/${player.playerid}.png`,
    }));

    // set fuse collection
    fuse.value.setCollection(players.value);
    console.log(players.value);
  } catch (error) {
    console.error('Error fetching players:', error);
  }
}

onMounted(fetchPlayers);
</script>

<style scoped lang="postcss">
.players-list {
  height: 90vh;
  display: flex;
  flex-direction: column;

  .scroller {
    height: 90vh;
    overflow: auto;
    position: relative;
    flex-grow: 1;
  }
}
</style>