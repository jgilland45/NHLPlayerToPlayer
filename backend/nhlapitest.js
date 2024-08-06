const API_NHLE = 'https://api.nhle.com/stats/rest'
const API_NHLE_WEB = 'https://api-web.nhle.com/v1'
const API_NHL_ASSETS_MUG = 'https://assets.nhle.com/mugs/nhl'
const API_NHL_ASSETS_LOGO = 'https://assets.nhle.com/logos/nhl/svg'

const fetchDataFromNHLE = async (endpoint) => {
    try {
        const response = await (await fetch(`${API_NHLE}/${endpoint}`)).json()
        console.log('Getting data from', `${API_NHLE}/${endpoint}`)
        return response.data
    } catch (err) {
        console.log(err)
    }
}

const fetchDataFromNHLEWeb = async (endpoint) => {
    try {
        const response = await (await fetch(`${API_NHLE_WEB}/${endpoint}`)).json()
        console.log('Getting data from', `${API_NHLE_WEB}/${endpoint}`)
        return response
    } catch (err) {
        console.log(err)
    }
}

const fetchDataFromNHLAssetsMug = async (endpoint) => {
    try {
        const response = await (await fetch(`${API_NHL_ASSETS_MUG}/${endpoint}`))
        console.log('Getting data from', `${API_NHL_ASSETS_MUG}/${endpoint}`)
        return response
    } catch (err) {
        console.log(err)
    }
}

const fetchDataFromNHLAssetsLogo = async (endpoint) => {
    try {
        const response = await (await fetch(`${API_NHL_ASSETS_LOGO}/${endpoint}`))
        console.log('Getting data from', `${API_NHL_ASSETS_LOGO}/${endpoint}`)
        return response
    } catch (err) {
        console.log(err)
    }
}

const formatPlayerArray = (playerArray, teamInfo, season) => {
    return playerArray.map(d => ({
        playerId: d["playerId"],
        teamId: teamInfo.id,
        season,
    }))
}

const getPlayersFromGame = async (gameID) => {
    try {
        const response = await fetchDataFromNHLEWeb(`gamecenter/${gameID}/boxscore`)
        const season = response.season;
        const homeTeamInfo = response.homeTeam
        const awayTeamInfo = response.awayTeam
        const homeForwards = formatPlayerArray(response.playerByGameStats.homeTeam.forwards, homeTeamInfo, season)
        const homeDefence = formatPlayerArray(response.playerByGameStats.homeTeam.defense, homeTeamInfo, season)
        const homeGoalies = formatPlayerArray(response.playerByGameStats.homeTeam.goalies, homeTeamInfo, season)
        const awayForwards = formatPlayerArray(response.playerByGameStats.awayTeam.forwards, awayTeamInfo, season)
        const awayDefence = formatPlayerArray(response.playerByGameStats.awayTeam.defense, awayTeamInfo, season)
        const awayGoalies = formatPlayerArray(response.playerByGameStats.awayTeam.goalies, awayTeamInfo, season)
        const homePlayers = homeForwards.concat(homeDefence, homeGoalies)
        const awayPlayers = awayForwards.concat(awayDefence, awayGoalies)
        return {
            homePlayers,
            awayPlayers,
        }
    } catch (err) {
        console.log(err)
    }
}

const mainDataFetcher = async () => {
    const allGamesRaw = await fetchDataFromNHLE('en/game');
    const allTeamsRaw = await fetchDataFromNHLE('en/team')
    const allRegularSeasonAndPlayoffGames = allGamesRaw.filter(game => game['gameType'] === 2 || game['gameType'] === 3)
    // console.log(allRegularSeasonAndPlayoffGames.filter(game => game["season"] === 20232024))
    const { homePlayers, awayPlayers } = await getPlayersFromGame(allRegularSeasonAndPlayoffGames[0].id)
    console.log('home:', homePlayers)
    console.log('away:', awayPlayers)
    homePlayers.concat(awayPlayers).forEach(player => {
        const teamTricode = allTeamsRaw.find(d => d.id === player.teamId)?.triCode
        console.log(`${API_NHL_ASSETS_MUG}/${player.season}/${teamTricode}/${player.playerId}.png`)
    })
}

mainDataFetcher()
