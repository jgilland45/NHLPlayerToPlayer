const API_NHLE = 'https://api.nhle.com'
const API_NHLE_WEB = 'https://api-web.nhle.com/v1'
const API_NHL_ASSETS = 'https://assets.nhle.com/mugs/nhl'

const fetchDataFromNHLE = async (endpoint) => {
    try {
        const response = await (await fetch(`${API_NHLE}/${endpoint}`)).json()
        return response.data
    } catch (err) {
        console.log(err)
    }
}

const fetchDataFromNHLEWeb = async (endpoint) => {
    try {
        const response = await (await fetch(`${API_NHLE_WEB}/${endpoint}`)).json()
        return response.data
    } catch (err) {
        console.log(err)
    }
}

const fetchDataFromNHLAssets = async (endpoint) => {
    try {
        const response = await (await fetch(`${API_NHL_ASSETS}/${endpoint}`)).json()
        return response.data
    } catch (err) {
        console.log(err)
    }
}

async function logMovies() {
    const response = await fetch("http://example.com/movies.json");
    const movies = await response.text();
    console.log(movies);
  }

console.log('hi')
console.log(logMovies())
