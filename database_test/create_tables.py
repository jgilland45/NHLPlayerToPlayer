import sqlite3

connection = None
cursor = None
dbpath = None
user = None

def connect(path):
    """
    Create the global cursor connected to the db, along with the current user

    :param path: the path to the database being used

    :returns cursor: the db cursor object
    """
    global connection, cursor, dbpath, user
    if connection is None:
        dbpath = path
        connection = sqlite3.connect(path)
        cursor = connection.cursor()
        cursor.execute(" PRAGMA foreign_keys=ON; ")
        # uncomment below for good debugging of query statements
        # connection.set_trace_callback(print)
        connection.commit()
    return cursor

def create_tables():
    """
    Creates the tables for the program, if they do not already exist
    """
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Players (
            playerid INT PRIMARY KEY
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Teams (
            teamid TEXT PRIMARY KEY
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Games (
            gameid TEXT PRIMARY KEY
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Player_Game (
            playerid INT,
            gameid TEXT,
            teamid TEXT,
            PRIMARY KEY (playerid, gameid, teamid),
            FOREIGN KEY (playerid) REFERENCES Players(playerid),
            FOREIGN KEY (gameid) REFERENCES Games(gameid),
            FOREIGN KEY (teamid) REFERENCES Teams(teamid)
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Player_Team (
            playerid INT,
            teamid TEXT,
            PRIMARY KEY (playerid, teamid),
            FOREIGN KEY (playerid) REFERENCES Players(playerid),
            FOREIGN KEY (teamid) REFERENCES Teams(teamid)
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Player_Info (
            playerid INT PRIMARY KEY,
            name TEXT,
            FOREIGN KEY (playerid) REFERENCES Players(playerid)
        );
    """)
    cursor.connection.commit()