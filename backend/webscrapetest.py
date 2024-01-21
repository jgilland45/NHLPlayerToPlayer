# for NHL stuff, refer back to https://www.youtube.com/watch?v=ygmeoyr8L2M&ab_channel=ActionBackers and https://www.youtube.com/watch?v=_xwV_-735hs&ab_channel=ActionBackers
# from course https://www.youtube.com/watch?v=WNvxR8RFzBg&ab_channel=freeCodeCamp.org
# create new Python environment using py -m venv myvenv

import requests
import time
import random
import re
import sqlite3
from bs4 import BeautifulSoup as bs
from datetime import date
# https://stackoverflow.com/questions/517923/what-is-the-best-way-to-remove-accents-normalize-in-a-python-unicode-string
from unidecode import unidecode

class Player:
    def __init__(self, name, url):
        self.name = name
        self.url = url
        self.teams = []
        self.teammates = []
        self.teammatePairTeams = {}

    def __str__(self):
        outputStr = f'Name: {self.name}  Teams: '
        for team in self.teams:
            outputStr = outputStr + f'{team}, '
        # for teammate in self.teammates:
        #     outputStr = outputStr + f'{teammate}, '
        return outputStr

    def __eq__(self, other):
        return self.url == other.url
    
    def __hash__(self):
        return hash(self.url)
    
    def addTeam(self, team):
        if (team not in self.teams):
            self.teams.append(team)

    def addTeammates(self, teammates):
        # concatenate teammate arrays
        self.teammates+=teammates
        # make array contain only unique elements
        self.teammates = list(set(self.teammates))
        self.teammates.pop(self.teammates.index(self))

    def addTeammatePairTeams(self, teammate, team):
        if (teammate.getURL() in self.teammatePairTeams.keys()):
            if (team not in self.teammatePairTeams[teammate.getURL()]):
                self.teammatePairTeams[teammate.getURL()].append(team)
        else:
            self.teammatePairTeams[teammate.getURL()] = [team]

    def getName(self):
        return self.name
    
    def getURL(self):
        return self.url

    def getTeams(self):
        return self.teams

    def getTeammates(self):
        return self.teammates
    
    def getTeammatePairTeams(self):
        return self.teammatePairTeams
    

def main():
    # loadPlayersToDatabase()

    # chooseTeammatesAndCheckIfTeammates()

    startTeammatePathGame()
    
        

def loadPlayersToDatabase():
    playersList = []
    gamesUrlList = []
    teamsList = []
    # yearsList = getAllYears()
    # for year in yearsList:
    #     print(getYearUrl(year))
    #     gamesUrlList = getAllGamesInYear(getYearUrl(year))
    #     print(gamesUrlList)
    yearList = {2015}
    # yearList = getAllYears()
    # nhlPlayerDB = createNHLPlayerDatabase()
    nhlPlayerDB = sqlite3.connect('nhlPlayers.db')
    for year in yearList:
        gamesUrlList = getAllGamesInYear(getYearUrl(year))
        numGamesGone = 0
        for gameUrl in gamesUrlList:
            getAllPlayersInGame(gameUrl, playersList, year)
            numGamesGone+=1
            print("Progess: " + str(numGamesGone) + "/1312")

    
    # f = open("players.txt", "a", encoding="utf-8")
        for player in playersList:
            for team in player.getTeams():
                if team not in teamsList:
                    teamsList.append(team)
                    addTeamToDatabase(nhlPlayerDB, team)
            # f.write(str(player))
            # f.write(" Teammates: ")
            # for teammate in player.getTeammates():
            #     f.write(teammate.getName() + ", ")
            # f.write('\n')
            # print(player)
            addPlayerToDatabase(nhlPlayerDB, player)
            addTeamsForPlayerToDatabase(nhlPlayerDB, player)
            addTeammatesAndTeamForPlayerToDatabase(nhlPlayerDB, player)
        nhlPlayerDB.commit()
    # f.close()
    nhlPlayerDB.close()

def chooseTeammatesAndCheckIfTeammates():
    nhlPlayerDB = sqlite3.connect('nhlPlayers.db')
    userInput = ""
    while (userInput != "exit"):
        teammate1Name = input("Enter first player's name: ")
        teammate2Name = input("Enter second player's name: ")
        teammate1Object = nhlPlayerDB.execute("Select URL FROM PLAYERS WHERE NAME=?", (teammate1Name,))
        teammate2Object = nhlPlayerDB.execute("Select URL FROM PLAYERS WHERE NAME=?", (teammate2Name,))
        teammate1URLObject = teammate1Object.fetchone()
        teammate2URLObject = teammate2Object.fetchone()
        if (teammate1URLObject == None or teammate2URLObject == None): continue
        teammate1URL = teammate1URLObject[0]
        teammate2URL = teammate2URLObject[0]
        teammatesOfTeammate1 = nhlPlayerDB.execute("SELECT t.URL FROM PLAYERS p INNER JOIN PLAYER_TEAMMATES_TEAMS pt ON pt.PLAYERURL = p.URL INNER JOIN PLAYERS t ON t.URL = pt.TEAMMATEURL WHERE PLAYERURL=?", (teammate1URL,))
        areTheyTeammates = False
        for x in teammatesOfTeammate1:
            areTheyTeammates = x == teammate2URLObject
            # print("Is x == teammate2? " + str(areTheyTeammates))
            if areTheyTeammates: break
        print("Are they teammates? " + str(areTheyTeammates))
        if (areTheyTeammates):
            relatedTeams = nhlPlayerDB.execute("SELECT TEAMNAME FROM PLAYER_TEAMMATES_TEAMS WHERE PLAYERURL=? AND TEAMMATEURL=?", (teammate1URL,teammate2URL))
            for relatedTeam in relatedTeams:
                # TODO: determine whether goalies that didn't play in the same game count as teammates
                # or if we keep the definition of "teammates" as they both were on the ice in the same game
                # this means that team who never pulled their goalies will not have goalie teammates
                print(relatedTeam[0])
        userInput = input("Type 'exit' to stop, type anything else to continue: ")
    nhlPlayerDB.close()

# opens and closes DB connection on its own
def startTeammatePathGame():
    nhlPlayerDB = sqlite3.connect('nhlPlayers.db')
    allPlayers = nhlPlayerDB.execute("Select * FROM PLAYERS").fetchall()
    startPlayerRandInt = random.randint(0,len(allPlayers)-1)
    endPlayerRandInt = random.randint(0,len(allPlayers)-1)
    while (endPlayerRandInt == startPlayerRandInt):
        endPlayerRandInt = random.randint(0,len(allPlayers)-1)
    # TODO: make sure to clarify start/end players if they have duplicate names
        # eg. sebastian aho
    startPlayer = allPlayers[startPlayerRandInt]
    endPlayer = allPlayers[endPlayerRandInt]
    print("Start player: " + startPlayer[1])
    print("End player: " + endPlayer[1])
    playerGuessed = False
    numGuesses = 0
    currentLeftPlayer = startPlayer
    while (not playerGuessed):
        teammateGuess = makeTeammateGuess(allPlayers, currentLeftPlayer)
        if (checkIfPlayerIsTeammate(currentLeftPlayer, teammateGuess)):
            relatedTeams = nhlPlayerDB.execute("SELECT TEAMNAME FROM PLAYER_TEAMMATES_TEAMS WHERE PLAYERURL=? AND TEAMMATEURL=?", (currentLeftPlayer[0],teammateGuess[0]))
            print("Yes! They both played for:")
            for relatedTeam in relatedTeams:
                print(relatedTeam[0])
            if (teammateGuess is endPlayer):
                playerGuessed = True
            else:
                currentLeftPlayer = teammateGuess
            numGuesses+=1
        else:
            print("Not a teammate! Guess again!")
    print("You got there in " + str(numGuesses) + " players!")
    nhlPlayerDB.close()
    playAgain = input("Type 'exit' to stop playing, and type anything else to play again.\n")
    if (playAgain.lower() != "exit"):
        startTeammatePathGame()

def makeTeammateGuess(allPlayers, currentLeftPlayer):
    allPlayerNamesNormalized = []
    for player in allPlayers:
        allPlayerNamesNormalized.append(unidecode(player[1]).lower())
    guessPlayer = input("Name a teammate of " + currentLeftPlayer[1] + ": ")
    guessPlayer = unidecode(guessPlayer).lower()
    while (guessPlayer not in allPlayerNamesNormalized):
        guessPlayer = input("Not found in database! Name a teammate: ")
        guessPlayer = unidecode(guessPlayer).lower()
    # https://stackoverflow.com/questions/6294179/how-to-find-all-occurrences-of-an-element-in-a-list
    indices = [i for i, x in enumerate(allPlayerNamesNormalized) if x == guessPlayer]
    playerIndex = -1
    if (len(indices) > 1):
        clarifyString = "Which one? Please type the number.\n"
        counter = 0
        for index in indices:
            clarifyString = clarifyString + str(counter) + " https://www.hockey-reference.com" + allPlayers[index][0] + "\n"
            counter+=1
        clarifyIndex = input(clarifyString)
        while ((not clarifyIndex.isdigit()) or (int(clarifyIndex) >= len(indices))):
            clarifyIndex = input("Please try again: " + clarifyString)
        clarifyIndex = int(clarifyIndex)
        playerIndex = indices[clarifyIndex]
    else:
        playerIndex = indices[0]
    guessPlayerObject = allPlayers[playerIndex]
    return guessPlayerObject

def checkIfPlayerIsTeammate(startPlayer, teammateGuess):
    nhlPlayerDB = sqlite3.connect('nhlPlayers.db')
    teammatesOfStartPlayer = nhlPlayerDB.execute("SELECT t.URL FROM PLAYERS p INNER JOIN PLAYER_TEAMMATES_TEAMS pt ON pt.PLAYERURL = p.URL INNER JOIN PLAYERS t ON t.URL = pt.TEAMMATEURL WHERE PLAYERURL=?", (startPlayer[0],)).fetchall()
    for teammate in teammatesOfStartPlayer:
        if (teammateGuess[0] == teammate[0]):
            return True
    return False



# got parallel tables idea from https://stackoverflow.com/questions/17371639/how-to-store-arrays-in-mysql
def createNHLPlayerDatabase():
    nhlPlayerDB = sqlite3.connect('nhlPlayers.db')

    nhlPlayerDB.execute("DROP TABLE IF EXISTS PLAYERS")
    nhlPlayerDB.execute('''CREATE TABLE PLAYERS
                    (URL TEXT PRIMARY KEY NOT NULL, 
                    NAME TEXT NOT NULL);''')
    
    nhlPlayerDB.execute("DROP TABLE IF EXISTS PLAYER_TEAMMATES")
    nhlPlayerDB.execute("DROP TABLE IF EXISTS PLAYER_TEAMMATES_TEAMS")
    nhlPlayerDB.execute('''CREATE TABLE PLAYER_TEAMMATES_TEAMS
                    (PLAYERURL TEXT NOT NULL, 
                    TEAMMATEURL TEXT NOT NULL,
                    TEAMNAME TEXT NOT NULL,
                    PRIMARY KEY(PLAYERURL, TEAMMATEURL, TEAMNAME));''')
    
    nhlPlayerDB.execute("DROP TABLE IF EXISTS TEAMS")
    nhlPlayerDB.execute('''CREATE TABLE TEAMS
                    (TEAMNAME TEXT NOT NULL PRIMARY KEY);''')
    
    nhlPlayerDB.execute("DROP TABLE IF EXISTS PLAYER_TEAMS")
    nhlPlayerDB.execute('''CREATE TABLE PLAYER_TEAMS
                    (PLAYERURL TEXT NOT NULL, 
                    TEAMNAME TEXT NOT NULL,
                    PRIMARY KEY(PLAYERURL, TEAMNAME));''')
    
    return nhlPlayerDB

# from https://stackoverflow.com/questions/4360593/python-sqlite-insert-data-from-variables-into-table
# unique entry ideas from https://stackoverflow.com/questions/3164505/mysql-insert-record-if-not-exists-in-table
def addPlayerToDatabase(database, player):
    database.execute("INSERT INTO PLAYERS SELECT * FROM (SELECT ?, ?) AS tmp WHERE NOT EXISTS (SELECT URL FROM PLAYERS WHERE URL=?) LIMIT 1", (player.getURL(), player.getName(), player.getURL()))

def addTeamToDatabase(database, team):
    database.execute("INSERT INTO TEAMS SELECT * FROM (SELECT ?) AS tmp WHERE NOT EXISTS (SELECT TEAMNAME FROM TEAMS WHERE TEAMNAME=?) LIMIT 1", (team, team))
    
def addTeamsForPlayerToDatabase(database, player):
    for team in player.getTeams():
        database.execute("INSERT OR REPLACE INTO PLAYER_TEAMS VALUES (?, ?)", (player.getURL(), team))

def addTeammatesAndTeamForPlayerToDatabase(database, player):
    for teammate in player.getTeammates():
        for team in player.getTeammatePairTeams()[teammate.getURL()]:
            database.execute("INSERT OR REPLACE INTO PLAYER_TEAMMATES_TEAMS VALUES (?, ?, ?)", (player.getURL(), teammate.getURL(), team))
    


def soupSetup(url):
    res = requests.get(url)
    soup = bs(res.content, 'html.parser')
    return soup


# gets first year from HockeyReferenceTable
def getNewestYear():
    url = "https://www.hockey-reference.com/leagues/"
    soup = soupSetup(url)
    time.sleep(random.randint(2,4))
    table = soup.find(id="league_index")
    tbody = table.find('tbody')
    tr_body = tbody.find('tr')
    th = tr_body.find('th')
    newestYear = th.get_text()
    newestYear = newestYear[:2] + newestYear[5:]
    return newestYear

def getTeam1Players(table, teamName, year, playersList):
    team = []
    tbody = table.find('tbody')
    for rows in tbody.findChildren('tr'):
        name = rows.findChild('td').findChild('a').get_text()
        playerID = rows.findChild('td').findChild('a')['href']
        # print(name)
        # print(playerID)
        player = Player(name, playerID)
        fullTeam = teamName + " " + str(year)
        if (player in playersList): 
            if (fullTeam not in playersList[playersList.index(player)].getTeams()):
                playersList[playersList.index(player)].addTeam(fullTeam)
        else:
            player.addTeam(fullTeam)
            playersList.append(player)
        team.append(player)
        # print(player)
        # time.sleep(random.randint(1,3))
    return team

def getTeam2Players(table, teamName, year, playersList):
    team = []
    tbody = table.find('tbody')
    for rows in tbody.findChildren('tr'):
        name = rows.findChild('td').findChild('a').get_text()
        playerID = rows.findChild('td').findChild('a')['href']
        # print(name)
        # print(playerID)
        player = Player(name, playerID)
        fullTeam = teamName + " " + str(year)
        if (player in playersList): 
            if (fullTeam not in playersList[playersList.index(player)].getTeams()):
                playersList[playersList.index(player)].addTeam(fullTeam)
        else:
            player.addTeam(fullTeam)
            playersList.append(player)
        team.append(player)
        # print(player)
        # time.sleep(random.randint(1,3))
    return team

def getAllPlayersInGame(gameUrl, playersList, year):
    baseURL = "https://www.hockey-reference.com"
    soup = soupSetup(gameUrl)
    time.sleep(random.randint(2,4))
    tables = soup.find_all('div', {'id': re.compile("^div.*skaters$")})
    teamNameDivs = soup.find_all('div', {'id': re.compile("^all.*skaters$")})
    team1Name = teamNameDivs[0].findChild('div', {'id': re.compile(".*skaters_sh$")}).findChild('h2').get_text()
    team2Name = teamNameDivs[1].findChild('div', {'id': re.compile(".*skaters_sh$")}).findChild('h2').get_text()
    team1 = getTeam1Players(tables[0].findChild('table'), team1Name, year, playersList)
    team2 = getTeam2Players(tables[1].findChild('table'), team2Name, year, playersList)
    for player in team1:
        playersList[playersList.index(player)].addTeammates(team1)
        for teammate in team1:
            playersList[playersList.index(player)].addTeammatePairTeams(teammate, team1Name + " " + str(year))
        # if (player not in playersList):
        #     playersList.append(player)
        # print(player)
    for player in team2:
        playersList[playersList.index(player)].addTeammates(team2)
        for teammate in team2:
            playersList[playersList.index(player)].addTeammatePairTeams(teammate, team2Name + " " + str(year))
        # if (player not in playersList):
        #     playersList.append(player)
        # print(player)
    return playersList

def getAllGamesInYear(yearUrl):
    baseURL = "https://www.hockey-reference.com"
    gamesUrlList = []
    soup = soupSetup(yearUrl)
    time.sleep(random.randint(2,4))
    table = soup.find(id="games")
    tbody = table.find('tbody')
    tr_body = tbody.find_all('tr')
    numGames = 0
    startGame = 0
    for tr in tr_body:
        numGames+=1
        if (numGames<(startGame)): continue
        th = tr.find('th')
        if (th.findChild("a")):
            gamesUrlList.append(baseURL + str(th.findChild("a")['href']))
            print(baseURL + str(th.findChild("a")['href']) + "   SUCCESS")
        # time.sleep(random.randint(3,5))
        print("numGamesLoaded: " + str(numGames) + "/1312")
        # if (numGames==(startGame + 600)): break
    return gamesUrlList

def getYearUrl(year):
    baseURL = "https://www.hockey-reference.com/"
    return baseURL + 'leagues/NHL_' + str(year) + '_games.html'

def getAllYears():
    yearsList = []
    for x in range(int(getNewestYear()), 1917, -1):
        if (x!=2005): 
            yearsList.append(x)
    return yearsList

if __name__ == '__main__':
    main()


