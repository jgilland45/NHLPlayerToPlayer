CREATE TABLE IF NOT EXISTS Players (
    playerid INT PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS Teams (
    teamid TEXT PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS Games (
    gameid TEXT PRIMARY KEY
);

-- INSERT INTO Players (playerid)
-- VALUES (8478493), (8481751), (8479406), (8474567);

-- INSERT INTO Teams (teamid)
-- VALUES ("MIN20232024"), ("BUF20232024");

-- INSERT INTO Games (gameid)
-- VALUES ("2023020204");

CREATE TABLE IF NOT EXISTS Player_Game (
    playerid INT,
    gameid TEXT,
    teamid TEXT,
    PRIMARY KEY (playerid, gameid, teamid),
    FOREIGN KEY (playerid) REFERENCES Players(playerid),
    FOREIGN KEY (gameid) REFERENCES Games(gameid),
    FOREIGN KEY (teamid) REFERENCES Teams(teamid)
);

CREATE TABLE IF NOT EXISTS Player_Team (
    playerid INT,
    teamid TEXT,
    PRIMARY KEY (playerid, teamid),
    FOREIGN KEY (playerid) REFERENCES Players(playerid),
    FOREIGN KEY (teamid) REFERENCES Teams(teamid)
);

CREATE TABLE IF NOT EXISTS Player_Info (
    playerid INT PRIMARY KEY,
    name TEXT,
    FOREIGN KEY (playerid) REFERENCES Players(playerid)
);