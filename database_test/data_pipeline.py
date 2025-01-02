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
        gameids.append(gameid)
    return gameids

def get_teams(tricodes):
    teams_list = []
    for tricode in tricodes:
        team_stats_URL = 'https://api-web.nhle.com/v1/club-stats-season/' + tricode
        response = requests.get(team_stats_URL)
        data = response.json()
        if len(data) == 0:
            continue
        team_years = [x['season'] for x in data]
        for year in team_years:
            teams_list.append(tricode + str(year))
    return teams_list

def get_all_team_tricodes():
    teams_URL = 'https://api.nhle.com/stats/rest/en/team'
    response = requests.get(teams_URL)
    data = response.json()['data']
    tricodes_list = []
    for tricode in data:
        tricodes_list.append(tricode['triCode'])
    return tricodes_list

def get_all_years():
    years_URL = 'https://api-web.nhle.com/v1/season'
    response = requests.get(years_URL)
    data = response.json()
    years_list = []
    for year in data:
        years_list.append(year)
    return years_list

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
    # create_tables.create_tables()

    # tricodes = get_all_team_tricodes()
    # teams = get_teams(tricodes)
    # for team in teams:
    #     db_inserts.insert_teamid(team)

    # gameids = get_all_gameids()
    # for gameid in gameids:
    #     db_inserts.insert_gameid(gameid)

    gameids = db_getters.get_all_games()
    
    for gameid in gameids:
        if int(gameid) >= 2021010082 and int(gameid) < 2026010082:
            insert_info_from_game(int(gameid))

if __name__ == "__main__":
    run()