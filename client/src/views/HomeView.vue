<template>
  <div class="bg-white">
    {{ wsResponse.message }}
  </div>
  <PlayerCardUsingID 
    :id="currentPlayer"
  />
  <PlayerCardUsingID
    v-for="guess in guesses"
    :id="guess"
  />
  <SearchWithResults 
    @click="playerClicked"
  />
</template>

<script setup lang="ts">
import { type Player } from '@/components/SearchWithResults.vue';
import { useWebSocket } from '@vueuse/core';
import { computed, ref, watch } from 'vue';

import SearchWithResults from '@/components/SearchWithResults.vue';
import PlayerCardUsingID from '@/components/PlayerCardUsingID.vue';

const game_id = 1;

const guesses = ref<number[]>([]);
const currentPlayer = ref<number>(0);

const { status, data, send, open, close } = useWebSocket(`ws://127.0.0.1:8000/ws/${game_id}`, {
  immediate: true,
});

const wsResponse = computed(() => JSON.parse(data.value));

const playerClicked = (player: Player) => {
  console.log(player);
  const wsSend = {
    action: "guess",
    payload: player.id,
  };
  send(JSON.stringify(wsSend));
}

watch(wsResponse, (newVal) => {
  if (!newVal) return;
  console.log('newVal: ', newVal);
  if (newVal.last_guess) {
    if (newVal.last_guess.correct) {
      guesses.value.push(newVal.last_guess.guessed);
      console.log(guesses.value);
    }
  }
  if (newVal.current_player) {
    currentPlayer.value = newVal.current_player;
  }
});

</script>

<style lang="postcss" scoped>
</style>
