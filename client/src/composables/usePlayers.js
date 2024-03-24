import { ref } from 'vue'
import { fetchDataFromApi } from '@/api/api'

const playersTable = ref()

const loadPlayersTable = async () => {
    const response = await fetchDataFromApi('players')
    playersTable.value = response
}

export default () => {
    if (!playersTable.value) {
        (async () => { await loadPlayersTable() })()
    }
    return playersTable
}
