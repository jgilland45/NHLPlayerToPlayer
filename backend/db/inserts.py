import time
from backend.db import manage_schema
import sqlite3

def insert_playerid(playerid):
    try:
        manage_schema.cursor.execute("""
            INSERT OR REPLACE INTO Players (playerid)
            VALUES (?);
        """, (playerid, ))
    except sqlite3.OperationalError:
        time.sleep(1)
        insert_playerid(playerid)
    manage_schema.cursor.connection.commit()

def insert_teamid(teamid):
    try:
        manage_schema.cursor.execute("""
            INSERT OR REPLACE INTO Teams (teamid)
            VALUES (?);
        """, (teamid, ))
    except sqlite3.OperationalError:
        time.sleep(1)
        insert_teamid(teamid)
    manage_schema.cursor.connection.commit()

def insert_gameid(gameid):
    try:
        manage_schema.cursor.execute("""
            INSERT OR REPLACE INTO Games (gameid)
            VALUES (?);
        """, (gameid, ))
    except sqlite3.OperationalError:
        time.sleep(1)
        insert_gameid(gameid)
    manage_schema.cursor.connection.commit()

def insert_player_game(playerid, gameid, teamid):
    try:
        manage_schema.cursor.execute("""
            INSERT OR REPLACE INTO Player_Game (playerid, gameid, teamid)
            VALUES (?, ?, ?);
        """, (playerid, gameid, teamid, ))
    except sqlite3.IntegrityError:
        insert_teamid(teamid)
    except sqlite3.OperationalError:
        time.sleep(1)
        insert_player_game(playerid, gameid, teamid)
    manage_schema.cursor.connection.commit()

def insert_player_info(playerid, name):
    try:
        manage_schema.cursor.execute("""
            INSERT OR REPLACE INTO Player_Info (playerid, name)
            VALUES (?, ?);
        """, (playerid, name, ))
        manage_schema.cursor.connection.commit()
    except sqlite3.OperationalError:
        time.sleep(1)
        insert_player_info(playerid, name)

def insert_player_team(playerid, teamid):
    try:
        manage_schema.cursor.execute("""
            INSERT OR REPLACE INTO Player_Team (playerid, teamid)
            VALUES (?, ?);
        """, (playerid, teamid, ))
    except sqlite3.IntegrityError as e:
        insert_teamid(teamid)
    except sqlite3.OperationalError:
        time.sleep(1)
        insert_player_team(playerid, teamid)
    manage_schema.cursor.connection.commit()