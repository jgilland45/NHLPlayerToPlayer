const API_NHLE = 'https://api.nhle.com/stats/rest'
const API_NHLE_WEB = 'https://api-web.nhle.com/v1'
const API_NHL_ASSETS_MUG = 'https://assets.nhle.com/mugs/nhl'
const API_NHL_ASSETS_LOGO = 'https://assets.nhle.com/logos/nhl/svg'

class Player {
    games = []
    constructor(playerId) {
        this.playerId = playerId
    }

    getPlayerId() {
        return this.playerId
    }

    getGames() {
        return this.games
    }

    addGameIfNotInList(game) {
        if (this.games.length === 0 || !this.games.find(d => d === game)) this.games.push(game)
    }
};

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

const formatPlayerArray = (playerArray, teamAbbr, gameId) => {
    return playerArray.map(d => ({
        playerId: d["playerId"],
        gameIdWithTeamAbbr: `${gameId}_${teamAbbr}`
    }))
}

const getPlayersFromGame = async (gameID) => {
    try {
        const response = await fetchDataFromNHLEWeb(`gamecenter/${gameID}/boxscore`)
        console.log(`${API_NHLE_WEB}/gamecenter/${gameID}/boxscore`)
        const gameId = response.id;
        const homeTeamAbbr = response.homeTeam.abbrev
        const awayTeamAbbr = response.awayTeam.abbrev
        const homeForwards = formatPlayerArray(response.playerByGameStats.homeTeam.forwards, homeTeamAbbr, gameId)
        const homeDefence = formatPlayerArray(response.playerByGameStats.homeTeam.defense, homeTeamAbbr, gameId)
        const homeGoalies = formatPlayerArray(response.playerByGameStats.homeTeam.goalies, homeTeamAbbr, gameId)
        const awayForwards = formatPlayerArray(response.playerByGameStats.awayTeam.forwards, awayTeamAbbr, gameId)
        const awayDefence = formatPlayerArray(response.playerByGameStats.awayTeam.defense, awayTeamAbbr, gameId)
        const awayGoalies = formatPlayerArray(response.playerByGameStats.awayTeam.goalies, awayTeamAbbr, gameId)
        const homePlayers = homeForwards.concat(homeDefence, homeGoalies)
        const awayPlayers = awayForwards.concat(awayDefence, awayGoalies)
        return {
            homePlayers,
            awayPlayers,
        }
    } catch (err) {
        console.log(err)
        return {
            homePlayers: [],
            awayPlayers: [],
        }
    }
}

const playersList = []

const mainDataFetcher = async () => {
    const allGamesRaw = await fetchDataFromNHLE('en/game')
    const allRegularSeasonAndPlayoffGames = allGamesRaw.filter(game => game['gameType'] === 2 || game['gameType'] === 3)
    const coolGames = allRegularSeasonAndPlayoffGames.filter(game => game["season"] === 19261927 || game["season"] === 19271928)
    for (let i = 0; i < coolGames.length; i++) {
        const { homePlayers, awayPlayers } = await getPlayersFromGame(coolGames[i].id)
        console.log('home:', homePlayers)
        console.log('away:', awayPlayers)
        homePlayers.concat(awayPlayers).forEach(player => {
            const foundPlayer = playersList.find(d => d.getPlayerId() === player.playerId)
            if (foundPlayer) {
                const foundPlayerIndex = playersList.findIndex(d => d.getPlayerId() === player.playerId)
                playersList[foundPlayerIndex].addGameIfNotInList(player.gameIdWithTeamAbbr)
            } else {
                const currPlayer = new Player(player.playerId)
                currPlayer.addGameIfNotInList(player.gameIdWithTeamAbbr)
                playersList.push(currPlayer)
            }
        })
    }
    const fs = require('node:fs');
    playersList.forEach(player => {
        fs.appendFile("./test.txt", `${player.getPlayerId()}: `, { flag: 'a' }, function (err) {
            if (err) throw err
        });
        player.getGames().forEach(game => {
            fs.appendFile("./test.txt", `${game}, `, { flag: 'a' }, function (err) {
                if (err) throw err
            });
        })
        fs.appendFile("./test.txt", "\n", { flag: 'a' }, function (err) {
            if (err) throw err
        });
    })
}


mainDataFetcher()
