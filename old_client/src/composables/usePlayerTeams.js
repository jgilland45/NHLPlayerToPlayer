import { ref } from 'vue'
import { fetchDataFromApi } from '@/api/api'

const playersTeamsTable = ref()

const loadPlayersTeamsTable = async () => {
    const response = await fetchDataFromApi('playersteams')
    playersTeamsTable.value = response
}

export default () => {
    if (!playersTeamsTable.value) {
        (async () => { await loadPlayersTeamsTable() })()
    }
    return playersTeamsTable
}
