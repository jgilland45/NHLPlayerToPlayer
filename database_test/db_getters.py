import create_tables
import requests

DEFAULT_IMAGE_URL = "https://assets.nhle.com/mugs/nhl/default-skater.png"

def get_all_players():
    create_tables.cursor.execute("""
        SELECT playerid, name
        FROM Player_Info;
    """)
    players = create_tables.cursor.fetchall()
    return [{"playerid": row[0], "name": row[1]} for row in players]

def get_all_playerids():
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

def get_year_of_most_recent_game_played():
    create_tables.cursor.execute("""
        SELECT distinct(gameid)
        FROM Player_Game
        ORDER BY gameid DESC
        LIMIT 1;
    """)
    gameid = create_tables.cursor.fetchone()
    return gameid[0][0:4]

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

def get_random_playerid_from_team_and_years(tricode, loweryear, upperyear):
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

def get_random_playerid_from_team(tricode):
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

def get_random_playerid_from_years(loweryear, upperyear):
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

def get_reg_and_playoff_teammates_of_player(playerid):
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

def get_reg_and_playoff_common_teams(player1, player2):
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

def get_teams_from_playerid(playerid):
    create_tables.cursor.execute("""
        SELECT teamid
        FROM Player_Team pi
        WHERE playerid = ?;
    """, (playerid, ))
    teams = create_tables.cursor.fetchall()
    return [x[0] for x in list(teams)]

def get_player_image_url(playerid: int) -> str:
    # Get all teamids for the player
    create_tables.cursor.execute("""
        SELECT teamid
        FROM Player_Team
        WHERE playerid = ?
    """, (playerid,))
    teams = create_tables.cursor.fetchall()

    if not teams:
        return DEFAULT_IMAGE_URL

    # Extract (team_tricode, season) and find most recent
    most_recent_team = None
    most_recent_season = 0

    for (teamid,) in teams:
        tricode = teamid[:3]
        try:
            season = int(teamid[-8:])  # extract 8 digits and convert
        except ValueError:
            continue  # skip bad data

        if season > most_recent_season:
            most_recent_season = season
            most_recent_team = tricode

    if not most_recent_team:
        return DEFAULT_IMAGE_URL

    # Build the image URL
    season_str = str(most_recent_season)
    url = f"https://assets.nhle.com/mugs/nhl/{season_str}/{most_recent_team}/{playerid}.png"

    # Optionally: check if the URL exists
    try:
        response = requests.head(url, timeout=2)
        if response.status_code == 404:
            return DEFAULT_IMAGE_URL
    except requests.RequestException:
        return DEFAULT_IMAGE_URL

    return url
