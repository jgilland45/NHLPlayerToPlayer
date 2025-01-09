import { ref } from 'vue'
import { fetchDataFromApi } from '@/api/api'

const gamesTable = ref()

const loadGamesTable = async () => {
    const response = await fetchDataFromApi('nhl/api/games')
    const intermediateResponse = response.data.map(d => ({
        id: d.id,
        type: d.gameType,
        season: d.season
    }))
    gamesTable.value = intermediateResponse
}

export default () => {
    if (!gamesTable.value) {
        (async () => { await loadGamesTable() })()
    }
    return gamesTable
}
