import { ref } from 'vue'
import { fetchDataFromApi } from '@/api/api'

const playersTable = ref()

const loadPlayersTable = async () => {
    const response = await fetchDataFromApi('players')
    const intermediateResponse = response
    playersTable.value = intermediateResponse.map(d => {
        const imgPartOfUrl = d.URL.slice(11, -5)
        const imgURL = `https://www.puckdoku.com/faces/${imgPartOfUrl}.jpg`
        return {
            ...d,
            IMGURL: imgURL
        }
    })
}

export default () => {
    if (!playersTable.value) {
        (async () => { await loadPlayersTable() })()
    }
    return playersTable
}
