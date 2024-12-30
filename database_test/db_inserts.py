import create_tables
import sqlite3

def insert_playerid(playerid):
    create_tables.cursor.execute("""
        INSERT OR REPLACE INTO Players (playerid)
        VALUES (?);
    """, (playerid, ))
    create_tables.cursor.connection.commit()

def insert_teamid(teamid):
    create_tables.cursor.execute("""
        INSERT OR REPLACE INTO Teams (teamid)
        VALUES (?);
    """, (teamid, ))
    create_tables.cursor.connection.commit()

def insert_gameid(gameid):
    create_tables.cursor.execute("""
        INSERT OR REPLACE INTO Games (gameid)
        VALUES (?);
    """, (gameid, ))
    create_tables.cursor.connection.commit()

def insert_player_game(playerid, gameid, teamid):
    try:
        create_tables.cursor.execute("""
            INSERT OR REPLACE INTO Player_Game (playerid, gameid, teamid)
            VALUES (?, ?, ?);
        """, (playerid, gameid, teamid, ))
    except sqlite3.IntegrityError:
        insert_teamid(teamid)
    create_tables.cursor.connection.commit()

def insert_player_info(playerid, name):
    create_tables.cursor.execute("""
        INSERT OR REPLACE INTO Player_Info (playerid, name)
        VALUES (?, ?);
    """, (playerid, name, ))
    create_tables.cursor.connection.commit()

def insert_player_team(playerid, teamid):
    try:
        create_tables.cursor.execute("""
            INSERT OR REPLACE INTO Player_Team (playerid, teamid)
            VALUES (?, ?);
        """, (playerid, teamid, ))
    except sqlite3.IntegrityError as e:
        insert_teamid(teamid)
    create_tables.cursor.connection.commit()