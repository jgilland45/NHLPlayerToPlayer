<template>
    <div class="single-player-daily-container">
        <div v-if="wonGame">
            You win!!
        </div>
        <button @click="guessRandomPlayer">Guess random player</button>
        <div class="playersContainer">
            <PlayerBlock
            class="player start"
            :player="startingPlayer">
            </PlayerBlock>
            <PlayerBlock
                v-for="player in guessedPlayers"
                :key="player"
                :player="player"
                class="player"
            >
            </PlayerBlock>
            <PlayerBlock
                class="player end"
                :player="endingPlayer">
            </PlayerBlock>
        </div>
        <div class="search-block">
            <form v-on:submit.prevent="onSubmit" id="search">
                Search <input name="query" v-model="searchQuery" class="search-bar">
            </form>
            <SearchBlock
                :data="allPossiblePlayers"
                :columns="gridColumns"
                :filterKey="searchQuery"
                @choose="guessPlayer">
            </SearchBlock>
        </div>
    </div>
</template>

<script setup>
import { ref, watch, watchEffect, computed, onMounted } from 'vue'
import { usePlayerToPlayerDailyStore } from '@/stores/playerToPlayerDaily'
import { fetchDataFromApi } from '@/api/api'
import SearchBlock from '@/components/SearchBlock.vue'
import PlayerBlock from '@/components/PlayerBlock.vue'

const wonGame = ref(false)

const playerToPlayerDailyStore = usePlayerToPlayerDailyStore()

const startingPlayer = computed(() => playerToPlayerDailyStore.startingPlayerInfo)
const endingPlayer = computed(() => playerToPlayerDailyStore.endingPlayerInfo)

const guessedPlayers = ref([])
const incorrectGuesses = ref([])
const gridColumns = ['url', 'name']
const searchQuery = ref('')
const currentPlayer = ref()
const currentPlayerTeammates = ref([])

// possible players are those that are not the starting player or a guessed player
const allPossiblePlayers = ref([])

const guessPlayer = (guessedPlayer) => {
  if (currentPlayerTeammates.value.find(x => x.TEAMMATEURL === guessedPlayer.url)) {
    guessedPlayers.value.push(guessedPlayer)
    incorrectGuesses.value = []
    currentPlayer.value = guessedPlayer
    console.log('found!')
  } else {
    incorrectGuesses.value.push(guessedPlayer)
    console.log('not found!')
    console.log(currentPlayerTeammates.value)
    return
  }
  if (guessedPlayer.url === endingPlayer.value.url) {
    wonGame.value = true
  }
  // https://stackoverflow.com/questions/5767325/how-can-i-remove-a-specific-item-from-an-array-in-javascript
  const playerIndex = allPossiblePlayers.value.indexOf(guessedPlayer)
  if (playerIndex > -1) {
    allPossiblePlayers.value.splice(playerIndex, 1)
  }
  searchQuery.value = ''
}

const guessRandomPlayer = () => {
  const randNum = Math.floor(Math.random() * playerToPlayerDailyStore.numTotalPlayers)
  const randPlayer = playerToPlayerDailyStore.allPlayers[randNum]
  guessedPlayers.value.push(randPlayer)
  // https://stackoverflow.com/questions/5767325/how-can-i-remove-a-specific-item-from-an-array-in-javascript
  const playerIndex = allPossiblePlayers.value.indexOf(randPlayer)
  if (playerIndex > -1) {
    allPossiblePlayers.value.splice(playerIndex, 1)
  }
}

const onSubmit = () => console.log('submitted form')

watchEffect(async () => {
  try {
    const playerData = await fetchDataFromApi('players')
    playerToPlayerDailyStore.setInitialPlayerData(playerData)
    playerToPlayerDailyStore.setStartAndEndPlayers()
    currentPlayer.value = playerToPlayerDailyStore.startingPlayerInfo
    allPossiblePlayers.value = playerToPlayerDailyStore.allPlayers
    // https://stackoverflow.com/questions/5767325/how-can-i-remove-a-specific-item-from-an-array-in-javascript
    const playerIndex = allPossiblePlayers.value.indexOf(playerToPlayerDailyStore.startingPlayerInfo)
    if (playerIndex > -1) {
      allPossiblePlayers.value.splice(playerIndex, 1)
    }
  } catch (err) {
    console.log('ERROR FETCHING DATA: ', err)
  }
})

watch(currentPlayer, async () => {
  try {
    currentPlayerTeammates.value = await fetchDataFromApi(`${currentPlayer.value.url}/teammates`)
  } catch (err) {
    console.log('ERROR FETCHING DATA: ', err)
  }
})

</script>

<style lang="postcss" scoped>
.single-player-daily-container {
    @apply flex flex-col flex-auto justify-center items-center gap-5;
    .playersContainer {
        @apply flex flex-col flex-auto;
        .player {
            @apply mt-3 pl-1 text-xl border-2 border-black;
        }
        .start {
            @apply bg-green-500;
        }
        .end {
            @apply bg-red-500;
        }
    }
    .search-block {
        @apply border p-2;
        .search-bar {
            @apply bg-gray-100 border border-black;
        }
    }
}
</style>
