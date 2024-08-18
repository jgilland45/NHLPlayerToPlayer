import sqlite3 from 'sqlite3';
import { open } from 'sqlite';
import _ from 'lodash-es';

let db;

// this is a top-level await 
await (async () => {
    // open the database
    db = await open({
        filename: './playersTEST.db',
        driver: sqlite3.Database
    })
})()

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

const addPlayerDataFromYearToDB = async (allGames, season) => {
    await db.run('CREATE TABLE IF NOT EXISTS players (playerid TEXT PRIMARY KEY, gameids TEXT)')
    const playersList = []
    const coolGames = allGames.filter(game => game["season"] === season)
    for (let i = 0; i < coolGames.length; i++) {
        const { homePlayers, awayPlayers } = await getPlayersFromGame(coolGames[i].id)
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
    for (let i = 0; i < playersList.length; i++) {
        const playerid = playersList[i].getPlayerId();
        const gameids = playersList[i].getGames();

        // Check if playerid exists
        const row = await db.get("SELECT gameids FROM players WHERE playerid = ?", [playerid], (err) => {
            if (err) {
                console.error(err.message);
                return;
            }
        })

        console.log('row: ', row)

        const currentGameIdsArray = row ? JSON.parse(row.gameids) : [];
        // unique union of new and existing gameids
        const updatedGameIdsArray = Array.from(new Set([...currentGameIdsArray, ...gameids]));

        const updatedGameIds = JSON.stringify(updatedGameIdsArray);

        if (row) {
            console.log('update existing row')
            // Update existing row
            await db.run("UPDATE players SET gameids = ? WHERE playerid = ?", [updatedGameIds, playerid], (err) => {
                if (err) {
                    console.error(err.message);
                    return;
                }
            });
        } else {
            console.log('insert new row')
            // Insert new row
            await db.run("INSERT INTO players (playerid, gameids) VALUES (?, ?)", [playerid, updatedGameIds], (err) => {
                if (err) {
                    console.error(err.message);
                    return;
                }
            });
        }
    }
    // const coolResult = await db.all('SELECT * FROM players WHERE playerid = "8471675"')
    // console.log(coolResult.map(d => ({ playerid: d.playerid, gameids: JSON.parse(d.gameids) })))
    // console.log(coolResult.map(d => JSON.parse(d.gameids).length))
}

const getPlayerDataForAllYears = async () => {
    const allGamesRaw = await fetchDataFromNHLE('en/game')
    const allRegularSeasonAndPlayoffGames = allGamesRaw.filter(game => game['gameType'] === 2 || game['gameType'] === 3)
    const allSeasons = await fetchDataFromNHLEWeb('season')
    for (let i = 0; i < allSeasons.length; i++) {
        await addPlayerDataFromYearToDB(allRegularSeasonAndPlayoffGames, allSeasons[i])
    }
}

const normalizeString = (string) => {
    return string.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase()
}

const getAllPlayers = async () => {
    return await fetchDataFromNHLE('en/players')
}

const getAllEntriesFromDB = async () => {
    const rows = await db.all("SELECT * FROM players");
    return rows.map(d => ({ playerid: d.playerid, gameids: JSON.parse(d.gameids) }))
}

const getAllGamesFromPlayer = async (playerid) => {
    // Check if playerid exists
    const row = await db.get("SELECT gameids FROM players WHERE playerid = ?", [playerid], (err) => {
        if (err) {
            console.error(err.message);
            return;
        }
    })
    return JSON.parse(row.gameids)
}

const getSharedTeams = async (...playersids) => {
    let playersgames = []
    for (let i = 0; i < playersids.length; i++) {
        const playergames = await getAllGamesFromPlayer(playersids[i])
        playersgames.push(playergames)
    }
    const commonGames = _.intersection(...playersgames)
    if (!commonGames.length) return []
    const commonTeams = _.uniq(commonGames.map(game => game.substring(0, 4) + '_' + game.substring(game.length - 3)))
    return commonTeams
}

const getTeammatesOfPlayer = async (playerid) => {
    const allPlayers = await getAllEntriesFromDB()
    const playerGames = await getAllGamesFromPlayer(playerid)
    const teammates = allPlayers.filter(d => !!(_.intersection(d.gameids, playerGames).length))
    return teammates
}

// SO I RAN THIS AND IT GAVE BACK ONE SINGULAR ENTRY, SO ANY NHL PLAYER CAN BE LINKED TO ANY OTHER NHL PLAYER
// DON'T RUN THIS AGAIN
const getAllTeammateLines = async () => {
    const allDbEntries = await getAllEntriesFromDB()
    console.log('loaded!')
    let allPossibilities = []
    for (let i = 0; i < allDbEntries.length; i++) {
        console.log('going through player', i + 1)
        if (!allPossibilities.length) {
            allPossibilities.push({ playerids: [allDbEntries[i].playerid], gameids: allDbEntries[i].gameids })
        } else {
            let foundMatch = false;
            for (let j = 0; j < allPossibilities.length; j++) {
                if (foundMatch) continue;
                // if there is overlap
                if (_.difference(allPossibilities[j].gameids, allDbEntries[i].gameids).length) {
                    // console.log('found match:', allDbEntries[i].playerid)
                    foundMatch = true;
                    allPossibilities[j].gameids = _.union(allPossibilities[j].gameids, allDbEntries[i].gameids)
                    allPossibilities[j].playerids.push(allDbEntries[i].playerid)
                }
            }
            if (!foundMatch) {
                // console.log('did not find match:', allDbEntries[i].playerid)
                allPossibilities.push({ playerids: [allDbEntries[i].playerid], gameids: allDbEntries[i].gameids })
            }
        }
    }
    return allPossibilities
}

// await getPlayerDataForAllYears();
const mbTeammates = await getTeammatesOfPlayer('8483158').then(d => d.map(dd => dd.playerid));
const mbTeammatesWithTeams = await Promise.all(mbTeammates.map(async (d) => {
    const commonTeam = await getSharedTeams('8483158', d)
    return ({
        playerid: d,
        commonteam: commonTeam,
    })
}))
console.log(mbTeammatesWithTeams)
// console.log(await getTeammatesOfPlayer('8483158').then(d => d.map(dd => dd.playerid)))
console.log(await getTeammatesOfPlayer('8478402').then(d => d.map(dd => dd.playerid)))

await db.close((err) => {
    if (err) {
        console.error('Error closing database connection:', err.message);
    } else {
        console.log('Database connection closed.');
    }
});
