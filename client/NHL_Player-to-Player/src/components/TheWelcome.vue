<template>
  <div class="game-container">
    <button @click="startGame">Start Game</button>
    <div class="player-connections">
      <div class="start-player">
        <span>Starting player:</span>
        <PlayerCard
          v-if="startPlayer"
          :player-name="startPlayer.name"
          :player-image-u-r-l="startPlayer.image_url"
        />
      </div>
      <div class="connecting-players">
        <PlayerCard
          v-for="player in connectedPlayers"
          :player-name="player.name"
          :player-image-u-r-l="player.image_url"
        />
      </div>
      <div class="end-player">
        <span>Ending player:</span>
        <PlayerCard
          v-if="endPlayer"
          :player-name="endPlayer.name"
          :player-image-u-r-l="endPlayer.image_url"
        />
      </div>
    </div>
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
    <p>{{ message }}</p>
    <p v-if="gameOver">🎉 Game Over!</p>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, watchEffect, onMounted } from 'vue';
import InputSearch from './InputSearch.vue';
import PlayerCard from './PlayerCard.vue';
import { useFuse } from '@vueuse/integrations/useFuse';
import axios from 'axios'

type Player = {
  playerid: number;
  name: string;
  image_url: string;
}

const DISPLAY_LIMIT = 50;
const DB_URL = "http://127.0.0.1:8000";
const SERVER_URL = "http://127.0.0.1:8080";

const sessionId = 'abc123';
const startPlayer = ref<Player | null>(null);
const endPlayer = ref<Player | null>(null);
const message = ref<string>('');
const gameOver = ref<boolean>(false);

const searchTerm = ref<string>('');
const players = ref<Player[]>([]);
const connectedPlayers = ref<Player[]>([]);

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

const startGame = async () => {
  const res = await axios.post(`${SERVER_URL}/start-game`, {
    session_id: sessionId
  })
  startPlayer.value = await getPlayerObjectFromID(res.data.start_player);
  endPlayer.value = await getPlayerObjectFromID(res.data.end_player);
}

const onPlayerChoiceClick = async (idx: number) => {
  console.log(players.value[idx]);
  
  const res = await axios.post(`${SERVER_URL}/make-guess`, {
    session_id: sessionId,
    guess: players.value[idx].playerid
  })

  if (res.data.result === 'correct') {
    message.value = `You connected the players in ${res.data.guesses} guesses!`;
    gameOver.value = true
  } else if (res.data.result === 'continue') {
    message.value = `Good! They both played for: ${res.data.teams.join(', ')}`;
    connectedPlayers.value.push(await getPlayerObjectFromID(res.data.next_player));
  } else {
    message.value = 'Nope, not a connection! Try again.';
  }
};

const getPlayerObjectFromID = async (playerid: number): Promise<Player> => {
  const response = await fetch(`${DB_URL}/player/${playerid}/name`);
  const data = await response.json();
  const playerName = data.name;
  const playerImageURL = `https://assets.nhle.com/mugs/nhl/latest/${playerid}.png`;
  return ({
    playerid,
    name: playerName,
    image_url: playerImageURL,
  });
};

async function fetchPlayers() {
  try {
    const response = await fetch(`${DB_URL}/players`);
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
.game-container {
  @apply flex flex-row flex-auto justify-center items-center w-full h-full;
  .player-connections {
    @apply flex flex-col justify-center items-center h-full max-h-[800px] overflow-auto;
  }

  .players-list {
    @apply flex flex-col w-full p-4 h-full max-h-[500px] overflow-auto;
  }
}
</style>