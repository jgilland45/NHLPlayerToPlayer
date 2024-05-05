import { defineStore } from 'pinia'
import usePlayers from '@/composables/usePlayers'
import usePlayerTeammates from '@/composables/usePlayerTeammates'
import usePlayersTeams from '@/composables/usePlayerTeams'
import useTeams from '@/composables/useTeams'
import { computed } from 'vue'

export const usePlayersStore = defineStore('playersStore', () => {
    const rawPlayers = usePlayers()
    const playersTeammates = usePlayerTeammates()
    const rawPlayersTeams = usePlayersTeams()
    const teams = useTeams()

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

    return {
        // players: rawPlayers,
        players,
        playersTeammates,
        teams
        // testPlayers: players
    }
})
