import create_tables
import db_getters
import data_pipeline
import requests

def replace_name_of_player(newname, playerid):
    create_tables.cursor.execute("""
        UPDATE Player_Info
        SET name = ?
        WHERE playerid = ?;
    """, (newname, playerid,))
    create_tables.cursor.connection.commit()

def get_abbreviated_name_from_playerid_and_gameid(playerid, gameid):
    game_url = f'https://api-web.nhle.com/v1/gamecenter/{gameid}/boxscore'
    try:
        response = requests.get(game_url)
        data = response.json()
        home_team = data['playerByGameStats']['homeTeam']
        away_team = data['playerByGameStats']['awayTeam']
        positions = ['forwards', 'defense', 'goalies']
        for position in positions:
            players = home_team[position]
            for player in players:
                if not player['playerId'] == playerid:
                    continue
                return player['name']['default']
            players = away_team[position]
            for player in players:
                if not player['playerId'] == playerid:
                    continue
                return player['name']['default']
    except:
        print(f"Couldn't find name for id {playerid}")
        return ""

def get_all_nameless_players_and_games():
    create_tables.cursor.execute("""
        SELECT min(gameid), pg.playerid
        FROM Player_Info pi, Player_Game pg
        WHERE name = ""
        AND pi.playerid = pg.playerid
        GROUP BY pg.playerid
        ORDER BY pg.playerid desc;
    """)
    pairs = create_tables.cursor.fetchall()
    return list(pairs)

def run():
    dbpath = "testdb.db"
    create_tables.connect(dbpath)

    player_game_pair = get_all_nameless_players_and_games()

    for pair in player_game_pair:
        new_name = get_abbreviated_name_from_playerid_and_gameid(pair[1], pair[0])
        replace_name_of_player(new_name, pair[1])
        print(f"player {pair[1]} has new name {new_name}")

if __name__ == "__main__":
    run()