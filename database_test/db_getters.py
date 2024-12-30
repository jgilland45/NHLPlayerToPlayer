import create_tables

def get_all_players():
    create_tables.cursor.execute("""
        SELECT playerid
        FROM Players;
    """)
    playerids = create_tables.cursor.fetchall()
    return [x[0] for x in list(playerids)]

def get_all_teams():
    create_tables.cursor.execute("""
        SELECT teamid
        FROM Teams;
    """)
    teamids = create_tables.cursor.fetchall()
    return [x[0] for x in list(teamids)]

def get_all_games():
    create_tables.cursor.execute("""
        SELECT gameid
        FROM Games;
    """)
    gameids = create_tables.cursor.fetchall()
    return [x[0] for x in list(gameids)]

# https://stackoverflow.com/questions/2279706/select-random-row-from-a-sqlite-table
def get_random_playerid():
    create_tables.cursor.execute("""
        SELECT playerid
        FROM Players
        ORDER BY RANDOM()
        LIMIT 1;
    """)
    randplayer = create_tables.cursor.fetchone()
    return randplayer[0]

def get_all_teammates_of_player(playerid):
    create_tables.cursor.execute("""
        SELECT DISTINCT(pg2.playerid)
        FROM Player_Game pg1, Player_Game pg2
        WHERE LOWER(pg1.playerid) = LOWER(?)
        AND pg1.gameid = pg2.gameid
        AND pg1.teamid = pg2.teamid;
    """, (playerid,))
    teammates = create_tables.cursor.fetchall()
    return [x[0] for x in list(teammates)]

def get_common_teams(player1, player2):
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

def get_playerids_from_name(name):
    create_tables.cursor.execute("""
        SELECT playerid
        FROM Player_Info pi
        WHERE LOWER(name) = LOWER(?);
    """, (name, ))
    playerids = create_tables.cursor.fetchall()
    return [x[0] for x in list(playerids)]

def get_name_from_playerid(playerid):
    create_tables.cursor.execute("""
        SELECT name
        FROM Player_Info pi
        WHERE playerid = ?;
    """, (playerid, ))
    name = create_tables.cursor.fetchone()
    return name[0]

