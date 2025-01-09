import { ref } from 'vue'
import { fetchDataFromApi } from '@/api/api'

const playersTeammatesTable = ref()

const loadPlayersTeammatesTable = async () => {
    const response = await fetchDataFromApi('playersteammates')
    playersTeammatesTable.value = response
}

export default () => {
    if (!playersTeammatesTable.value) {
        (async () => { await loadPlayersTeammatesTable() })()
    }
    return playersTeammatesTable
}
