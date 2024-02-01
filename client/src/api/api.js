// import axios from 'axios'

const API_BASE_URL = 'http://127.0.0.1:3000'

export const fetchDataFromApi = async (endpoint) => {
  try {
    const response = await (await fetch(`${API_BASE_URL}/${endpoint}`)).json()
    return response.data
  } catch (err) {
    console.log(err)
  }
}
