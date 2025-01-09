import create_tables
import db_getters
import db_inserts

import requests
import concurrent.futures
import sqlite3

def get_name_from_playerid(playerid):
    player_url = f'https://api-web.nhle.com/v1/player/{playerid}/landing'
    try:
        response = requests.get(player_url)
        data = response.json()
        first_name = data['firstName']['default']
        last_name = data['lastName']['default']
        return first_name + " " + last_name
    except:
        print(f"Couldn't find name for id {playerid}")
        return ""

def get_players_in_game(gameid):
    game_url = f'https://api-web.nhle.com/v1/gamecenter/{gameid}/boxscore'

    try:
        response = requests.get(game_url)
        data = response.json()
        home_team = data['playerByGameStats']['homeTeam']
        home_team_tricode = data['homeTeam']['abbrev']
        away_team = data['playerByGameStats']['awayTeam']
        away_team_tricode = data['awayTeam']['abbrev']
        season = data['season']
        positions = ['forwards', 'defense', 'goalies']
        player_game_info = []
        for position in positions:
            players = home_team[position]
            for player in players:
                player_game_info.append({
                    'playerid': player['playerId'],
                    'gameid': gameid,
                    'teamid': home_team_tricode + str(season),
                    })
            players = away_team[position]
            for player in players:
                player_game_info.append({
                    'playerid': player['playerId'],
                    'gameid': gameid,
                    'teamid': away_team_tricode + str(season),
                    })
        return player_game_info
    except:
        print(f"skipped game {gameid}")
        return []

def get_all_gameids():
    games_URL = 'https://api.nhle.com/stats/rest/en/game'
    response = requests.get(games_URL)
    data = response.json()['data']
    gameids = []
    for datum in data:
        gameid = datum['id']
        gameids.append(str(gameid))
    return gameids

def insert_info_from_game(gameid):
    players = get_players_in_game(gameid)
    theseplayerids = []
    thesegameids = []
    theseteamids = []
    for player in players:
        theseplayerids.append(player['playerid'])
        thesegameids.append(player['gameid'])
        theseteamids.append(player['teamid'])
    for pid in theseplayerids:
        db_inserts.insert_playerid(pid)
    for i, _ in enumerate(players):
        db_inserts.insert_player_game(theseplayerids[i], thesegameids[i], theseteamids[i])
        db_inserts.insert_player_info(theseplayerids[i], get_name_from_playerid(theseplayerids[i]))
        db_inserts.insert_player_team(theseplayerids[i], theseteamids[i])
    print(f"Inserted all information from game {gameid}\n")

def run():
    dbpath = "testdb.db"
    create_tables.connect(dbpath)

    all_gameids = get_all_gameids()

    # get most recent year since postponed games use same old gameid
    most_recent_game_played_year = db_getters.get_year_of_most_recent_game_played()
    
    for gameid in all_gameids:
        if gameid >= (int(most_recent_game_played_year)*1000000):
            insert_info_from_game(int(gameid))

if __name__ == "__main__":
    run()