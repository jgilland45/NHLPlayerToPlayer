import { defineStore } from 'pinia'
import usePlayers from '@/composables/usePlayers'
import usePlayerTeammates from '@/composables/usePlayerTeammates'
import usePlayersTeams from '@/composables/usePlayerTeams'
import useTeams from '@/composables/useTeams'
import useGames from '@/composables/useGames'
import { fetchDataFromApi } from '@/api/api'
import { computed, watch } from 'vue'

export const usePlayersStore = defineStore('playersStore', () => {
    const rawPlayers = usePlayers()
    const playersTeammates = usePlayerTeammates()
    const rawPlayersTeams = usePlayersTeams()
    const teams = useTeams()
    const games = useGames()

    // Semaphore to control concurrent API requests
    const concurrencyLimit = 1000 // Adjust as per your requirements
    let currentConcurrency = 0
    const requestQueue = []

    // acc stands for accumulator
    const uniquePlayersTeams = computed(() => {
        if (rawPlayersTeams.value) {
            return rawPlayersTeams.value.reduce((acc, player) => {
                const existingPlayer = acc.find(p => p.PLAYERURL === player.PLAYERURL)

                if (existingPlayer) {
                    existingPlayer.TEAMNAMES.push(player.TEAMNAME)
                } else {
                    acc.push({ PLAYERURL: player.PLAYERURL, TEAMNAMES: [player.TEAMNAME] })
                }
                return acc
            }, [])
        } else return []
    })

    const players = computed(() => uniquePlayersTeams.value.map(d => ({
        URL: d.PLAYERURL,
        NAME: rawPlayers.value.find(dd => dd.URL === d.PLAYERURL).NAME,
        TEAMNAMES: d.TEAMNAMES,
        IMGURL: rawPlayers.value.find(dd => dd.URL === d.PLAYERURL).IMGURL
    })))

    const regularSeasonAndPlayoffGames = computed(() => {
        if (!games.value) return []
        return games.value.filter(d => d.type === 2 || d.type === 3)
    })

    // Process the request queue
    const processQueue = async () => {
        if (currentConcurrency >= concurrencyLimit || requestQueue.length === 0) return

        currentConcurrency++
        const request = requestQueue.shift()

        try {
            const gameData = await fetchDataFromApi(`nhl/api/games/${request.id}`)
            request.resolve(gameData)
        } catch (error) {
            request.reject(error)
        } finally {
            currentConcurrency--
            processQueue() // Process next request in the queue
        }
    }

    // Define computed property for dataFromGames
    const dataFromGames = computed(() => {
        if (!regularSeasonAndPlayoffGames.value) return []

        regularSeasonAndPlayoffGames.value.forEach(game => {
            // Create a promise for each game ID and push it to the queue
            const promise = new Promise((resolve, reject) => {
                requestQueue.push({ id: game.id, resolve, reject })
            })
        })

        // Start processing the queue
        processQueue()

        // Return an array of promises that resolve to game data
        return requestQueue.map(request => request.promise)
    })

    // const fetchDataWithRetry = async (id, retries = 3, delay = 1000) => {
    //     try {
    //         const response = await fetch(`nhl/api/games/${id}`)
    //         return await response.json()
    //     } catch (error) {
    //         if (retries > 0) {
    //             await new Promise(resolve => setTimeout(resolve, delay))
    //             return fetchDataWithRetry(id, retries - 1, delay * 2)
    //         }
    //         throw error
    //     }
    // }

    // const dataFromGames = computed(() => {
    //     if (!regularSeasonAndPlayoffGames.value) return []

    //     const promises = regularSeasonAndPlayoffGames.value.map(game =>
    //         fetchDataWithRetry(game.id)
    //     )

    //     return Promise.all(promises)
    // })

    // watch(regularSeasonAndPlayoffGames, () => {
    //     if (!regularSeasonAndPlayoffGames.value) dataFromGames.value = []
    //     dataFromGames.value = regularSeasonAndPlayoffGames.value.map(async d => {
    //         const gameData = await fetchDataFromApi(`nhl/api/games/${d.id}`)
    //         return gameData
    //     })
    // })

    watch(dataFromGames, d => console.log('games:', d), { immediate: true })

    return {
        // players: rawPlayers,
        players,
        playersTeammates,
        teams
        // testPlayers: players
    }
})
