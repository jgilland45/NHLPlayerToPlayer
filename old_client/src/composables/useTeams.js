import { ref } from 'vue'
import { fetchDataFromApi } from '@/api/api'

const teamsTable = ref()

const loadTeamsTable = async () => {
    const response = await fetchDataFromApi('teams')
    teamsTable.value = response
}

export default () => {
    if (!teamsTable.value) {
        (async () => { await loadTeamsTable() })()
    }
    return teamsTable
}
