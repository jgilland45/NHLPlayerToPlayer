<template>
  <div
    v-if="loading"
    class="loading"
  >
    <p>Loading teammate graph... please wait!</p>
  </div>
  <div
    v-if="noLinkPopups.length"
    class="no_link_to_player"
  >
    <NoLinkToPlayer
      v-for="popup in noLinkPopups"
      :key="popup.id"
      :player-name="popup.player.name"
    />
  </div>
  <div
    class="game_container"
    :class="{
      is_loading: loading,
    }"
  >
    <button @click="startGame">Start Game</button>
    <div class="player_connections">
      <PlayerCard
        v-if="startPlayer"
        :player-name="startPlayer.name"
        :player-image-u-r-l="startPlayer.image_url"
      />
      <div class="connecting_players">
        <div
          v-for="(_, i) in connections"
          class="single_player_connection"
        >
          <TeamConnectionBundle
            v-if="connections.length > i"
            :team-connections="connections[i]"
          />
          <span>↓</span>
          <PlayerCard
            v-if="connectedPlayers.length > i"
            :player-name="connectedPlayers[i].name"
            :player-image-u-r-l="connectedPlayers[i].image_url"
          />
        </div>
      </div>
      <PlayerCard
        v-if="endPlayer"
        :player-name="endPlayer.name"
        :player-image-u-r-l="endPlayer.image_url"
      />
    </div>
    <div class="players_list">
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
    <button
      v-if="gameOver"
      @click="playAgain"
    >
      Play Again
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, watchEffect, onMounted } from 'vue';
import InputSearch from './InputSearch.vue';
import PlayerCard from './PlayerCard.vue';
import TeamConnectionBundle, {type TeamConnection } from './TeamConnectionBundle.vue';
import NoLinkToPlayer from './NoLinkToPlayer.vue';
import { useFuse } from '@vueuse/integrations/useFuse';
import axios from 'axios'

type Player = {
  playerid: number;
  name: string;
  image_url: string;
}

type PopupEntry = {
  id: number;
  player: Player;
};

const DISPLAY_LIMIT = 50;
const DB_URL = "http://127.0.0.1:8000";
const SERVER_URL = "http://127.0.0.1:8080/single-player";

const sessionId = 'abc123';
const startPlayer = ref<Player | null>(null);
const endPlayer = ref<Player | null>(null);
const message = ref<string>('');
const polling = ref(false);
const gameOver = ref<boolean>(false);
const graphStatus = ref('building');
const loading = ref(true);
const searchTerm = ref<string>('');
const players = ref<Player[]>([]);
const connectedPlayers = ref<Player[]>([]);
const connections = ref<TeamConnection[][]>([]);
const noLinkPopups = ref<PopupEntry[]>([]);
const popupCounter = ref<number>(0);

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
    session_id: sessionId,
  });
  startPlayer.value = await getPlayerObjectFromID(res.data.start_player);
  endPlayer.value = await getPlayerObjectFromID(res.data.end_player);
}

const onPlayerChoiceClick = async (idx: number) => {
  console.log(players.value[idx]);
  
  await axios.post(`${SERVER_URL}/make-guess`, {
    session_id: sessionId,
    guess: players.value[idx].playerid
  });

  // this polls the server for whether the guess was correct or not
  pollResponse();
};

const playAgain = async () => {
  const res = await axios.post(`${SERVER_URL}/play-again`, {
    session_id: sessionId,
    play_again: true,
  });

  // Replace old game state with new one
  startPlayer.value = await getPlayerObjectFromID(res.data.start_player);
  endPlayer.value = await getPlayerObjectFromID(res.data.end_player);
  message.value = '';
  searchTerm.value = '';
  gameOver.value = false;
  connectedPlayers.value = [];
  connections.value = [];

  pollGraphStatus();
};

const pollResponse = async () => {
  if (polling.value) return;
  polling.value = true;

  const check = async () => {
    try {
      const res = await axios.get(`${SERVER_URL}/check-response`, {
        params: { session_id: sessionId }
      });

      if (res.data.result === 'waiting') {
        setTimeout(check, 100)  // Try again in 100ms
      } else {
        handleGameResponse(res.data);
        polling.value = false;
      }
    } catch (err) {
      console.error("Polling error", err);
      polling.value = false;
    }
  }

  check();
};

const handleGameResponse = async (data: any) => {
  if (data.result === 'not_a_teammate') {
    message.value = '❌ Not a teammate!';
    popupCounter.value++;
    const id = popupCounter.value;
    noLinkPopups.value.push({
      id,
      player: await getPlayerObjectFromID(data.player),
    });
    setTimeout(() => {
      noLinkPopups.value = noLinkPopups.value.filter(p => p.id !== id);
    }, 2500);
  } else if (data.result === 'already_used') {
    message.value = '⚠️ Already guessed that player.';
  } else if (data.result === 'over_limit') {
    message.value = '🚫 Team overuse limit reached.';
  } else if (data.result === 'correct') {
    let shortestPath = await getShortestPath();
    let shortestPathPlayerObjects = []
    for (let id of shortestPath) {
      shortestPathPlayerObjects.push((await getPlayerObjectFromID(id)).name)
    }
    message.value = `🎉 You won in ${data.guesses} guesses! Shortest path: ${shortestPathPlayerObjects.join('->')}`;
    connections.value.push(await getTeamInfoFromCommonTeams(data.teams, data.strikes));
    gameOver.value = true;
    searchTerm.value = '';
  } else if (data.result === 'continue') {
    message.value = `✅ Correct! They both played for: ${data.teams.join(', ')}`;
    connectedPlayers.value.push(await getPlayerObjectFromID(data.next_player));
    connections.value.push(await getTeamInfoFromCommonTeams(data.teams, data.strikes));
    searchTerm.value = '';
  } else if (data.result === 'waiting') {
    message.value = 'Waiting for result...';
  } else {
    message.value = '⚠️ Unknown response.';
  }
};

const getShortestPath = async (): Promise<number[]> => {
  const res = await axios.get(`${SERVER_URL}/shortest-path`, {
    params: { player1: startPlayer.value?.playerid, player2: endPlayer.value?.playerid }
  });
  return res.data.path;
};

const getTeamInfoFromCommonTeams = async (teams: string[], strikes: number[]): Promise<TeamConnection[]> => {
  let allTeamConnections: TeamConnection[] = [];
  for (let [i, team] of teams.entries()) {
    const tri_code = team.slice(0, 3);
    const years = team.slice(3, team.length);
    const res = await axios.get(`${DB_URL}/team/logo`, {
      params: { team_tricode: tri_code, year: years }
    });
    const logo = res.data.logo;
    const name = res.data.name + " " + years.slice(0, 4) + "-" + years.slice(4, years.length);
    const numStrikes = strikes[i];
    allTeamConnections.push({
      teamName: name,
      numStrikes,
      teamLogoURL: logo,
    });
  }
  return allTeamConnections;
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

const pollGraphStatus = async () => {
  try {
    const res = await axios.get(`${SERVER_URL}/graph-status`);
    graphStatus.value = res.data.status;

    if (res.data.status !== 'ready') {
      setTimeout(pollGraphStatus, 300); // try again in 300ms
    } else {
      loading.value = false;
    }
  } catch (err) {
    console.error("Graph polling failed:", err);
    setTimeout(pollGraphStatus, 1000);
  }
};


onMounted(() => {
  fetchPlayers();
  pollGraphStatus();
});
</script>

<style scoped lang="postcss">
.loading {
  @apply absolute w-full h-full top-0 flex items-center justify-center text-white;
}
.no_link_to_player {
  @apply absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-white text-black;
}
.game_container {
  @apply flex flex-col flex-auto justify-center items-center w-full h-full;

  &.is_loading {
    @apply select-none blur-lg pointer-events-none;
  }

  .player_connections {
    @apply flex flex-col justify-center items-center h-full max-h-[800px] overflow-auto text-white;

    .connecting_players {
      @apply overflow-auto;

      .single_player_connection {
        @apply flex flex-col justify-center items-center; 
      }
    }
  }

  .players_list {
    @apply flex flex-col w-full p-4 h-full max-h-[500px] overflow-auto;
  }
}
</style>