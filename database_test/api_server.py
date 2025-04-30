from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import create_tables
import db_getters

# run using: `uvicorn api_server:app --reload --host 0.0.0.0 --port 8000`

app = FastAPI()

# Allow your Vue frontend to access the API (VERY IMPORTANT)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connect to your SQLite database
create_tables.connect("./testdb.db")

@app.get("/players")
def read_players():
    return {"players": db_getters.get_all_players()}

@app.get("/playerids")
def read_playerids():
    return {"players": db_getters.get_all_playerids()}

@app.get("/teams")
def read_teams():
    return {"teams": db_getters.get_all_teams()}

@app.get("/games")
def read_games():
    return {"games": db_getters.get_all_games()}

@app.get("/player/random")
def get_random_player(tricode: str = '', loweryear: int = 0, upperyear: int = 0):
    if tricode == '':
        if upperyear != 0 and loweryear != 0:
            return {"playerid": db_getters.get_random_playerid_from_years(loweryear, upperyear)}
        else:
            return {"playerid": db_getters.get_random_playerid()}
    else:
        if upperyear != 0 and loweryear != 0:
            return {"playerid": db_getters.get_random_playerid_from_team_and_years(tricode, loweryear, upperyear)}
        else:
            return {"playerid": db_getters.get_random_playerid_from_team(tricode)}

@app.get("/player/{playerid}/name")
def get_player_name(playerid: int):
    return {"name": db_getters.get_name_from_playerid(playerid)}

@app.get("/player/{playerid}/teams")
def get_player_teams(playerid: int):
    return {"teams": db_getters.get_teams_from_playerid(playerid)}

@app.get("/player/{playerid}/teammates")
def get_player_teams(playerid: int, gametype: str = "all"):
    if gametype == "all":
        return {"teammates": db_getters.get_all_teammates_of_player(playerid)}
    else:
        return {"teammates": db_getters.get_reg_and_playoff_teammates_of_player(playerid)}

@app.get("/teams/common")
def get_player_teams(player1: int, player2: int, gametype: str = "all"):
    if gametype == "all":
        return {"teammates": db_getters.get_common_teams(player1, player2)}
    else:
        return {"teammates": db_getters.get_reg_and_playoff_common_teams(player1, player2)}
