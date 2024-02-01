<template>
  <button @click="guessPlayer">Guess random player</button>
  <div class="playersContainer">
    <div class="player">
      {{ startingPlayer }}
    </div>
    <div
      v-for="player in guessedPlayers"
      :key="player"
      class="player"
    >
      {{ player }}
    </div>
    <div class="player">
      {{ endingPlayer }}
    </div>
  </div>
</template>

<script setup>
import { ref, watch, watchEffect, computed, onMounted } from 'vue'
import { usePlayerToPlayerDailyStore } from '@/stores/playerToPlayerDaily'
import { fetchDataFromApi } from '@/api/api'

const playerToPlayerDailyStore = usePlayerToPlayerDailyStore()

const startingPlayer = computed(() => playerToPlayerDailyStore.startingPlayerInfo)
const endingPlayer = computed(() => playerToPlayerDailyStore.endingPlayerInfo)

const guessedPlayers = ref([])

const guessPlayer = () => {
  const randNum = Math.floor(Math.random() * playerToPlayerDailyStore.numTotalPlayers)
  const randName = playerToPlayerDailyStore.allPlayerNames[randNum]
  guessedPlayers.value.push(randName)
}

watchEffect(async () => {
  try {
    const playerData = await fetchDataFromApi('players')
    playerToPlayerDailyStore.setInitialPlayerData(playerData)
    playerToPlayerDailyStore.setStartAndEndPlayers()
  } catch (err) {
    console.log('ERROR FETCHING DATA: ', err)
  }
})

</script>

<style lang="css" scoped>
.playersContainer {
  flex: 1 1 auto;
  flex-direction: column;
  position: absolute;
}
.player {
  width: 100%;
  margin-left: auto;
  margin-right: auto;
  margin-top: 10px;
  padding-left: 5px;
  font-size: 20px;
  border: 2px solid black;
}
</style>
