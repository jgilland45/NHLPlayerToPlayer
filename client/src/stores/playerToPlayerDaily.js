import { defineStore } from 'pinia'
import { ref } from 'vue'

export const usePlayerToPlayerDailyStore = defineStore('playerToPlayerDailyStore', () => {
  const startingPlayerInfo = ref({})
  const endingPlayerInfo = ref({})
  const allPlayerUrls = []
  const allPlayerNames = []
  const numTotalPlayers = ref(0)

  const setInitialPlayerData = (data) => {
    for (const player of data) {
      allPlayerUrls.push(player.URL)
      allPlayerNames.push(player.NAME)
      console.log(allPlayerUrls[numTotalPlayers.value])
      console.log(allPlayerNames[numTotalPlayers.value])
      numTotalPlayers.value++
    }
  }

  const setStartAndEndPlayers = () => {
    const startingRandNum = Math.floor(Math.random() * numTotalPlayers.value)
    let endingRandNum = 0
    do {
      endingRandNum = Math.floor(Math.random() * numTotalPlayers.value)
    } while (endingRandNum === startingRandNum)
    console.log(startingRandNum)
    console.log(endingRandNum)
    startingPlayerInfo.value = allPlayerNames[startingRandNum]
    endingPlayerInfo.value = allPlayerNames[endingRandNum]
    console.log(startingPlayerInfo.value)
    console.log(endingPlayerInfo.value)
  }

  const getPlayerByUrl = (url) => {
    return allPlayerNames[allPlayerUrls.indexOf(url)]
  }

  return {
    startingPlayerInfo,
    endingPlayerInfo,
    allPlayerUrls,
    allPlayerNames,
    numTotalPlayers,
    setInitialPlayerData,
    setStartAndEndPlayers,
    getPlayerByUrl
  }
})
