<template>
  <InputSearch
    class="search"
    v-model="inputText"
  />
  <PlayerCard
    v-for="player in players"
    :player-name="player.full_name"
    :player-image-u-r-l="player.photo_url"
  />
</template>

<script setup lang="ts">
import InputSearch from '@/components/InputSearch.vue';
import PlayerCard from '@/components/PlayerCard.vue';
import { ref, watch } from 'vue';
import { debounce } from 'lodash-es';

type Player = {
  id: number;
  full_name: string;
  photo_url: string;
}

const API_URL = `http://127.0.0.1:8000/players/search/`;

const inputText = ref<string>("");
const players = ref<Player[]>([]);

watch(inputText, debounce(async (newVal: string) => {
  if (!newVal) {
    players.value = [];
    return;
  }
  const url = `${API_URL}${newVal}`;
  const rawPlayerData = await (await fetch(url)).json();
  const mappedPlayers = rawPlayerData.map((player) => {
    const image_url = `https://assets.nhle.com/mugs/nhl/latest/${player.id}.png`;
    return {
      id: player.id,
      full_name: player.full_name,
      photo_url: image_url,
    }
  });
  console.log(mappedPlayers);
  players.value = mappedPlayers;
}, 250));

</script>

<style lang="postcss" scoped>
.search {
  @apply h-10 bg-white;
}
</style>
