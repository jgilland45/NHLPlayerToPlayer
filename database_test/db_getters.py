import create_tables
import requests
import threading

lock = threading.Lock()

DEFAULT_IMAGE_URL = "https://assets.nhle.com/mugs/nhl/default-skater.png"

def get_all_players():
    try:
        lock.acquire(True)
        create_tables.cursor.execute("""
            SELECT playerid, name
            FROM Player_Info;
        """)
        players = create_tables.cursor.fetchall()
        return [{"playerid": row[0], "name": row[1]} for row in players]

    finally:
        lock.release()

def get_all_playerids():
    try:
        lock.acquire(True)
        create_tables.cursor.execute("""
            SELECT playerid
            FROM Players;
        """)
        playerids = create_tables.cursor.fetchall()
        return [x[0] for x in list(playerids)]

    finally:
        lock.release()

def get_all_teams():
    try:
        lock.acquire(True)
        create_tables.cursor.execute("""
            SELECT teamid
            FROM Teams;
        """)
        teamids = create_tables.cursor.fetchall()
        return [x[0] for x in list(teamids)]

    finally:
        lock.release()

def get_all_games():
    try:
        lock.acquire(True)
        create_tables.cursor.execute("""
            SELECT gameid
            FROM Games;
        """)
        gameids = create_tables.cursor.fetchall()
        return [x[0] for x in list(gameids)]

    finally:
        lock.release()

def get_year_of_most_recent_game_played():
    try:
        lock.acquire(True)
        create_tables.cursor.execute("""
            SELECT distinct(gameid)
            FROM Player_Game
            ORDER BY gameid DESC
            LIMIT 1;
        """)
        gameid = create_tables.cursor.fetchone()
        return gameid[0][0:4]

    finally:
        lock.release()

# https://stackoverflow.com/questions/2279706/select-random-row-from-a-sqlite-table
def get_random_playerid():
    try:
        lock.acquire(True)
        create_tables.cursor.execute("""
            SELECT playerid
            FROM Players
            ORDER BY RANDOM()
            LIMIT 1;
        """)
        randplayer = create_tables.cursor.fetchone()
        return randplayer[0]

    finally:
        lock.release()

def get_random_playerid_from_team_and_years(tricode, loweryear, upperyear):
    try:
        lock.acquire(True)
        true_tricode = tricode + "%"
        create_tables.cursor.execute("""
            SELECT playerid
            FROM Player_Game
            WHERE LOWER(teamid) LIKE ?
            AND CAST(SUBSTR(teamid, LENGTH(teamid) - 7) AS INTEGER) >= ?
            AND CAST(SUBSTR(teamid, LENGTH(teamid) - 7) AS INTEGER) <= ?
            ORDER BY RANDOM()
            LIMIT 1;
        """, (true_tricode, loweryear, upperyear,))
        randplayer = create_tables.cursor.fetchone()
        return randplayer[0]

    finally:
        lock.release()

def get_random_playerid_from_team(tricode):
    try:
        lock.acquire(True)
        true_tricode = tricode + "%"
        create_tables.cursor.execute("""
            SELECT playerid
            FROM Player_Game
            WHERE LOWER(teamid) LIKE ?
            ORDER BY RANDOM()
            LIMIT 1;
        """, (true_tricode,))
        randplayer = create_tables.cursor.fetchone()
        return randplayer[0]

    finally:
        lock.release()

def get_random_playerid_from_years(loweryear, upperyear):
    try:
        lock.acquire(True)
        create_tables.cursor.execute("""
            SELECT playerid
            FROM Player_Game
            WHERE CAST(SUBSTR(teamid, LENGTH(teamid) - 7) AS INTEGER) >= ?
            AND CAST(SUBSTR(teamid, LENGTH(teamid) - 7) AS INTEGER) <= ?
            ORDER BY RANDOM()
            LIMIT 1;
        """, (loweryear, upperyear,))
        randplayer = create_tables.cursor.fetchone()
        return randplayer[0]

    finally:
        lock.release()

def get_all_teammates_of_player(playerid):
    try:
        lock.acquire(True)
        create_tables.cursor.execute("""
            SELECT DISTINCT(pg2.playerid)
            FROM Player_Game pg1, Player_Game pg2
            WHERE LOWER(pg1.playerid) = LOWER(?)
            AND pg1.gameid = pg2.gameid
            AND pg1.teamid = pg2.teamid;
        """, (playerid,))
        teammates = create_tables.cursor.fetchall()
        return [x[0] for x in list(teammates)]

    finally:
        lock.release()

def get_common_teams(player1, player2):
    try:
        lock.acquire(True)
        create_tables.cursor.execute("""
            SELECT DISTINCT(pg1.teamid)
            FROM Player_Game pg1, Player_Game pg2
            WHERE pg1.playerid = ?
            AND pg2.playerid = ?
            AND pg1.gameid = pg2.gameid
            AND pg1.teamid = pg2.teamid;
        """, (player1, player2, ))
        teams = create_tables.cursor.fetchall()
        return [x[0] for x in list(teams)]

    finally:
        lock.release()

def get_reg_and_playoff_teammates_of_player(playerid):
    try:
        lock.acquire(True)
        create_tables.cursor.execute("""
            SELECT DISTINCT(pg2.playerid)
            FROM Player_Game pg1, Player_Game pg2
            WHERE LOWER(pg1.playerid) = LOWER(?)
            AND pg1.gameid = pg2.gameid
            AND pg1.teamid = pg2.teamid
            AND (pg1.gameid like "____02%"
            OR pg1.gameid like "____03%");
        """, (playerid,))
        teammates = create_tables.cursor.fetchall()
        return [x[0] for x in list(teammates)]

    finally:
        lock.release()

def get_reg_and_playoff_common_teams(player1, player2):
    try:
        lock.acquire(True)
        create_tables.cursor.execute("""
            SELECT DISTINCT(pg1.teamid)
            FROM Player_Game pg1, Player_Game pg2
            WHERE pg1.playerid = ?
            AND pg2.playerid = ?
            AND pg1.gameid = pg2.gameid
            AND pg1.teamid = pg2.teamid
            AND (pg1.gameid like "____02%"
            OR pg1.gameid like "____03%");
        """, (player1, player2, ))
        teams = create_tables.cursor.fetchall()
        return [x[0] for x in list(teams)]

    finally:
        lock.release()

def get_playerids_from_name(name):
    try:
        lock.acquire(True)
        create_tables.cursor.execute("""
            SELECT playerid
            FROM Player_Info pi
            WHERE LOWER(name) = LOWER(?);
        """, (name, ))
        playerids = create_tables.cursor.fetchall()
        return [x[0] for x in list(playerids)]

    finally:
        lock.release()

def get_name_from_playerid(playerid):
    try:
        lock.acquire(True)
        create_tables.cursor.execute("""
            SELECT name
            FROM Player_Info pi
            WHERE playerid = ?;
        """, (playerid, ))
        name = create_tables.cursor.fetchone()
        return name[0]

    finally:
        lock.release()

def get_teams_from_playerid(playerid):
    try:
        lock.acquire(True)
        create_tables.cursor.execute("""
            SELECT teamid
            FROM Player_Team pi
            WHERE playerid = ?;
        """, (playerid, ))
        teams = create_tables.cursor.fetchall()
        return [x[0] for x in list(teams)]

    finally:
        lock.release()
