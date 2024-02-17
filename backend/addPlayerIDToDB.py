import sqlite3
import requests
from unidecode import unidecode

class TeamNameAndTricode:
    def __init__(self):
        self.name = None
        self.triCode = None
        self.id = None

def main():
    listOfTeamInfo = []
    gamesList = []
    playersList = []
    listOfTeamInfo = getAllTeams()
    for team in listOfTeamInfo:
        gamesList = getAllGamesFromTeams(team)
        break
    for game in gamesList:
        players = getPlayersFromGame(game)
        # for player in players:
        #     if player not in playersList:
        #         playersList.append(player)
    
def getAllYears():
    yearsList = []
    for x in range(2024, 1917, -1):
        if (x!=2005): 
            yearsList.append(x)
    return yearsList

def getAllTeams():
    teamsURL = 'https://api.nhle.com/stats/rest/en/team'
    response = requests.get(teamsURL)
    data = response.json()["data"]
    teamInfo = []
    for i, datum in enumerate(data):
        thisTeamInfo = TeamNameAndTricode()
        thisTeamInfo.name = unidecode(datum['fullName'])
        thisTeamInfo.triCode = datum['triCode']
        thisTeamInfo.id = datum['id']
        teamInfo.append(thisTeamInfo)
    return teamInfo

def getAllGamesFromTeams(team):
    allYears = getAllYears()
    allGames = []
    allGameIDs = []
    for i, year in enumerate(allYears):
        if (i < (len(allYears) - 1)):
            if (year == 2006):
                teamURL = 'https://api-web.nhle.com/v1/club-schedule-season/' + team.triCode + '/' + '2005' + str(year)
            else:
                teamURL = 'https://api-web.nhle.com/v1/club-schedule-season/' + team.triCode + '/' + str(allYears[i+1]) + str(year)
        else:
            teamURL = 'https://api-web.nhle.com/v1/club-schedule-season/' + team.triCode + '/' + '1917' + str(year)
        print(teamURL)
        response = requests.get(teamURL)
        for game in response.json()['games']:
            if game['id'] not in allGameIDs:
                allGameIDs.append(game['id'])
                allGames.append(game)
    return allGames
    # nhlPlayerDB = sqlite3.connect('nhlPlayers.db')
    # nhlPlayerDB.execute()
    # nhlPlayerDB.execute('''UPDATE PLAYER_TEAMS
    # SET PLAYERNAME
    # ''')

def getPlayersFromGame(game):
    gameURL = 'https://api-web.nhle.com/v1/gamecenter/' + str(game['id']) + '/play-by-play'
    response = requests.get(gameURL)
    print(response.json())
    return ''



    
if __name__ == '__main__':
    main()