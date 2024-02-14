import { defineStore } from 'pinia'
import { ref } from 'vue'

export const usePlayerToPlayerDailyStore = defineStore('playerToPlayerDailyStore', () => {
  const startingPlayerInfo = ref({})
  const endingPlayerInfo = ref({})
  const allPlayers = []
  const numTotalPlayers = ref(0)

  const setInitialPlayerData = (data) => {
    for (const player of data) {
      allPlayers.push({ url: player.URL, name: player.NAME })
      console.log(allPlayers[numTotalPlayers.value].url)
      console.log(allPlayers[numTotalPlayers.value].name)
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
    startingPlayerInfo.value = allPlayers[startingRandNum]
    endingPlayerInfo.value = allPlayers[endingRandNum]
    console.log(startingPlayerInfo.value)
    console.log(endingPlayerInfo.value)
  }

  const getPlayerByUrl = (url) => {
    return allPlayers.find(x => x.url === url)
  }

  return {
    startingPlayerInfo,
    endingPlayerInfo,
    allPlayers,
    numTotalPlayers,
    setInitialPlayerData,
    setStartAndEndPlayers,
    getPlayerByUrl
  }
})
