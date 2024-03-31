import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'
import usePlayers from '@/composables/usePlayers'
import usePlayerTeammates from '@/composables/usePlayerTeammates'

export const usePlayerToPlayerDailyStore = defineStore('playerToPlayerDailyStore', () => {
    const players = usePlayers()
    const playersTeammates = usePlayerTeammates()

    const allPlayers = computed(() => players.value)
    const allPlayersTeammates = computed(() => playersTeammates.value)

    const numTotalPlayers = computed(() => allPlayers.value ? allPlayers.value.length : 0)

    const searchQuery = ref('')
    const wonGame = ref(false)

    const guessedPlayers = ref([])
    const incorrectGuesses = ref([])

    const randNum1 = ref(Math.random())
    const randNum2 = ref(Math.random())

    const startingRandNum = computed(() => numTotalPlayers.value ? Math.floor(randNum1.value * numTotalPlayers.value) : 0)
    const endingRandNum = computed(() => {
        if (numTotalPlayers.value) {
            while (randNum1.value === randNum2.value) {
                randNum2.value = Math.random()
            }
            const currEndingRandNum = Math.floor(randNum2.value * numTotalPlayers.value)
            return currEndingRandNum
        }
        return 0
    })

    const startingPlayer = computed(() => {
        if (allPlayers.value) {
            return allPlayers.value[startingRandNum.value]
        }
        return {}
    })
    const endingPlayer = computed(() => {
        if (allPlayers.value) {
            return allPlayers.value[endingRandNum.value]
        }
        return {}
    })

    const currentPlayer = ref(startingPlayer.value)
    const currentPlayerTeammates = computed(() => allPlayersTeammates.value.filter(d => d.PLAYERURL === currentPlayer.value.URL))

    // possible players are those that are not the starting player or a guessed player
    const allPossiblePlayers = computed(() => {
        if (allPlayers.value) {
            const currPossiblePlayers = [...allPlayers.value]
            // https://stackoverflow.com/questions/5767325/how-can-i-remove-a-specific-item-from-an-array-in-javascript
            const startingPlayerIndex = currPossiblePlayers.indexOf(startingPlayer.value)
            if (startingPlayerIndex > -1) {
                currPossiblePlayers.splice(startingPlayerIndex, 1)
            }
            for (const p in guessedPlayers) {
                const playerIndex = currPossiblePlayers.indexOf(p.value)
                if (playerIndex > -1) {
                    currPossiblePlayers.splice(playerIndex, 1)
                }
            }
            return currPossiblePlayers
        }
        return []
    })

    const guessRandomPlayer = () => {
        const randNum = Math.floor(Math.random() * numTotalPlayers.value)
        const randPlayer = allPlayers.value[randNum]
        guessedPlayers.value.push(randPlayer)
        // https://stackoverflow.com/questions/5767325/how-can-i-remove-a-specific-item-from-an-array-in-javascript
        const playerIndex = allPossiblePlayers.value.indexOf(randPlayer)
        if (playerIndex > -1) {
            allPossiblePlayers.value.splice(playerIndex, 1)
        }
    }

    const guessPlayer = (guessedPlayer) => {
        if (currentPlayerTeammates.value.find(x => x.TEAMMATEURL === guessedPlayer.URL)) {
            guessedPlayers.value.push(guessedPlayer)
            incorrectGuesses.value = []
            currentPlayer.value = guessedPlayer
            console.log('found!')
        } else {
            incorrectGuesses.value.push(guessedPlayer)
            console.log('not found!')
            return
        }
        if (guessedPlayer.URL === endingPlayer.value.URL) {
            wonGame.value = true
        }
        // https://stackoverflow.com/questions/5767325/how-can-i-remove-a-specific-item-from-an-array-in-javascript
        const playerIndex = allPossiblePlayers.value.indexOf(guessedPlayer)
        if (playerIndex > -1) {
            allPossiblePlayers.value.splice(playerIndex, 1)
        }
        searchQuery.value = ''
    }

    const getPlayerByUrl = (url) => {
        return allPlayers.value.find(x => x.url === url)
    }

    watch(startingPlayer, (newP, oldP) => {
        if (Object.keys(oldP).length === 0) {
            currentPlayer.value = newP
        }
    })

    return {
        startingPlayer,
        endingPlayer,
        allPlayers,
        numTotalPlayers,
        wonGame,
        searchQuery,
        allPossiblePlayers,
        guessedPlayers,

        getPlayerByUrl,
        guessRandomPlayer,
        guessPlayer
    }
})
