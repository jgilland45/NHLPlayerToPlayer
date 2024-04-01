import { defineStore } from 'pinia'
import usePlayers from '@/composables/usePlayers'
import usePlayerTeammates from '@/composables/usePlayerTeammates'
import usePlayersTeams from '@/composables/usePlayerTeams'
import useTeams from '@/composables/useTeams'

export const usePlayersStore = defineStore('playersStore', () => {
    const players = usePlayers()
    const playersTeammates = usePlayerTeammates()
    const playersTeams = usePlayersTeams()
    const teams = useTeams()

    return {
        players,
        playersTeammates,
        playersTeams,
        teams
    }
})
