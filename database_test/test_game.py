import create_tables
import db_getters
from enum import Enum
import time
from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import random
import threading

# run using: `uvicorn test_game:app --reload --host 0.0.0.0 --port 8080`

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

TEAM_USE_LIMIT = 3

# Global state (for simplicity)
sessions = {}

class GuessRequest(BaseModel):
    session_id: str
    guess: int

class StartRequest(BaseModel):
    session_id: str

class PlayAgainRequest(BaseModel):
    session_id: str
    play_again: bool

class GameType(Enum):
    SINGLE = 1
    BATTLE = 2

class Player:
    skips = 1
    time = 1
    listteam = 1
    def use_skip(self):
        self.skips-=1
    def use_time(self):
        self.time-=1
    def use_listteam(self):
        self.listteam-=1
    def get_skip(self):
        return self.skips
    def get_time(self):
        return self.time
    def get_listteam(self):
        return self.listteam
    
@app.post("/start-game")
def start_game(req: StartRequest):
    """
    Initializes a new single-player connect game and stores session state.
    """
    session_id = req.session_id
    create_tables.connect("testdb.db")

    start_id = db_getters.get_random_playerid_from_years(20152016, 20242025)
    end_id = db_getters.get_random_playerid_from_years(20152016, 20242025)
    while end_id == start_id:
        end_id = db_getters.get_random_playerid_from_years(20152016, 20242025)

    sessions[session_id] = {
        "start": start_id,
        "end": end_id,
        "current": start_id,
        "locked": {start_id: True},
        "guessed_teams": {},
        "guesses": 0,
        "last_guess": None,
        "last_response": None,
        "play_again": None
    }

    # Start the backend game loop in a separate thread
    threading.Thread(target=single_player_connect_game, args=(session_id,), daemon=True).start()

    return {
        "start_player": start_id,
        "end_player": end_id,
    }

@app.post("/make-guess")
def make_singleplayer_guess(req: GuessRequest):
    """
    Processes a single teammate guess for the given session.
    """
    s = sessions.get(req.session_id)
    if not s:
        return {"error": "Session not found"}

    print(f"Received guess playerid: ${req.guess}")
    teammate_guess = req.guess  # simplify for now
    teammates = db_getters.get_all_teammates_of_player(s["current"])
    if teammate_guess not in teammates:
        return {"result": "not_a_teammate"}

    if s["locked"].get(teammate_guess):
        return {"result": "already_used"}

    # Check team limit
    over_limit = False
    teams = db_getters.get_common_teams(teammate_guess, s["current"])
    for t in teams:
        s["guessed_teams"][t] = s["guessed_teams"].get(t, 0) + 1
        if s["guessed_teams"][t] > TEAM_USE_LIMIT:
            over_limit = True
    if over_limit:
        return {"result": "over_limit"}

    s["current"] = teammate_guess
    s["locked"][teammate_guess] = True
    s["guesses"] += 1

    if teammate_guess == s["end"]:
        return {"result": "correct", "guesses": s["guesses"]}

    return {
        "result": "continue",
        "next_player": teammate_guess,
        "teams": teams,
    }

@app.get("/check-response")
def check_response(session_id: str):
    session = sessions.get(session_id)
    if not session:
        return {"error": "Session not found"}

    if "last_response" in session and session["last_response"] is not None:
        response = session["last_response"]
        session["last_response"] = None  # clear after sending
        return response

    return {"result": "waiting"}

@app.post("/play-again")
def play_again(req: PlayAgainRequest):
    session = sessions.get(req.session_id)
    if not session:
        return {"error": "Session not found"}

    session["play_again"] = req.play_again
    return {"status": "ok"}


def make_teammate_guess(currentLeftPlayer, inputted_player=None):
    if inputted_player is None:
        guess_player = input("Name a teammate of " + db_getters.get_name_from_playerid(currentLeftPlayer) + ": ")
    else:
        guess_player = inputted_player
    found_players = db_getters.get_playerids_from_name(guess_player)
    while (len(found_players) == 0):
        guess_player = input("Not found in database! Name a teammate: ")
        found_players = db_getters.get_playerids_from_name(guess_player)
    if (len(found_players) > 1):
        clarify_string = "Which one? Please type the number.\n"
        for index, playerid in enumerate(found_players):
            clarify_string = clarify_string + str(index) + " " + str(playerid) + "\n"
        clarify_index = input(clarify_string)
        while ((not clarify_index.isdigit()) or (int(clarify_index) >= len(found_players))):
            clarify_index = input("Please try again: " + clarify_string)
        clarify_index = int(clarify_index)
        found_player = found_players[clarify_index]
    else:
        found_player = found_players[0]
    return found_player

def handle_player_guess(current_left_player_teammates, current_left_player, locked_players, guessed_teams, inputted_player):
    teammateGuess = make_teammate_guess(current_left_player, inputted_player)
    if (teammateGuess in current_left_player_teammates):
        try:
            if locked_players[teammateGuess]:
                print(f"Cannot use {db_getters.get_name_from_playerid(teammateGuess)} since they were already used")
                return current_left_player
        except:
            pass
        relatedTeams = db_getters.get_common_teams(teammateGuess, current_left_player)
        for relatedTeam in relatedTeams:
            try:
                guessed_teams[relatedTeam]+=1
            except:
                guessed_teams[relatedTeam] = 1
            if guessed_teams[relatedTeam] > TEAM_USE_LIMIT:
                print(f"Cannot use this player - over team limit for team {relatedTeam}")
                return current_left_player
        print("Yes! They both played for:")
        for relatedTeam in relatedTeams:
            print(relatedTeam)
        current_left_player = teammateGuess
        locked_players[current_left_player] = 1
        return current_left_player
    else:
        print("Not a teammate! Guess again!")
    return current_left_player

def battle_turn_options(current_left_player_teammates, current_left_player, locked_players, guessed_teams, player, time_start, duration):
    turn_text = f"""
    Please type a teammate of {db_getters.get_name_from_playerid(current_left_player)} OR use one of the following powerups: {'time ' if player.get_time() else ''}{'list ' if player.get_listteam() else ''}{'skip ' if player.get_skip() else ''}
    You have {duration - (time.time() - time_start)}s left.
    """
    choice = input(turn_text)
    if time.time() - time_start > duration:
        print("Out of time!")
        return -1, []
    if choice.lower() == 'time':
        player.use_time()
        print("DOING TIME EXTEND")
        current_left_player, current_left_player_teammates = battle_turn_options(current_left_player_teammates, current_left_player, locked_players, guessed_teams, player, time_start, duration + 10)
        return current_left_player, current_left_player_teammates
    elif choice.lower() == 'list':
        player.use_listteam()
        teams_of_player = db_getters.get_teams_from_playerid(current_left_player)
        print(f"{db_getters.get_name_from_playerid(current_left_player)} has played for the following teams: {teams_of_player}\n")
        current_left_player, current_left_player_teammates = battle_turn_options(current_left_player_teammates, current_left_player, locked_players, guessed_teams, player, time_start, duration)
        return current_left_player, current_left_player_teammates
    elif choice.lower() == 'skip':
        player.use_skip()
        print("DOING SKIP")
        # no need for self call since this ends turn
        print(f"current_left_player: {current_left_player}")
        print(f"current_left_player_teammates: {current_left_player_teammates}")
        return current_left_player, current_left_player_teammates
    else:
        currentLeftPlayer = handle_player_guess(current_left_player_teammates, current_left_player, locked_players, guessed_teams, choice)
        print(f"locked players: {locked_players}")
        print(f"guessed teams: {guessed_teams}")
        if currentLeftPlayer == current_left_player:
            print("Not a valid teammate or option. Try again!")
            current_left_player, current_left_player_teammates = battle_turn_options(current_left_player_teammates, current_left_player, locked_players, guessed_teams, player, time_start, duration)
            return current_left_player, current_left_player_teammates
        current_left_player_teammates = db_getters.get_all_teammates_of_player(currentLeftPlayer)
        return currentLeftPlayer, current_left_player_teammates

def battle_game(settings):
    intro_text = """
    Welcome!
    This is a two-player game, where you will take turns naming teammates.
    Each player only has one life, so if you cannot name a teammate in time, you lose!
    Each player has powerups, including listing the teams a player played for, adding extra time, and skipping a guess.
    Each team for a given year can only be used up to 3 times.
    Have fun!
    """
    print(f"{intro_text}\n")
    dbpath = "testdb.db"
    create_tables.connect(dbpath)
    start_playerid = db_getters.get_random_playerid_from_years(20152016, 20242025)
    player1_turn = True
    print("Start player: " + db_getters.get_name_from_playerid(start_playerid))
    player1 = Player()
    player2 = Player()
    guessed_teams = {}
    locked_players = {}
    current_left_player = start_playerid
    locked_players[current_left_player] = 1
    current_left_player_teammates = db_getters.get_all_teammates_of_player(current_left_player)
    while True:
        print(f"Player {'1' if player1_turn else '2'}'s turn.\n")
        current_left_player, current_left_player_teammates = battle_turn_options(current_left_player_teammates, current_left_player, locked_players, guessed_teams, player1 if player1_turn else player2, time.time(), 20)
        if current_left_player == -1:
            print(f"Player {'1' if player1_turn else '2'} ran out of time. Player {'2' if player1_turn else '1'} wins!!")
            break
        player1_turn = not player1_turn

def single_player_connect_game(session_id: str):
    print(f"[{session_id}] Starting single player game...")
    dbpath = "testdb.db"
    create_tables.connect(dbpath)
    game = sessions.get(session_id)
    if not game:
        print(f"[{session_id}] Session not found.")
        return
    start_playerid = game["start"]
    end_playerid = game["end"]

    currentLeftPlayer = start_playerid
    playerGuessed = False
    numGuesses = 0
    locked_players = {currentLeftPlayer: True}
    guessed_teams = {}
    current_left_player_teammates = db_getters.get_all_teammates_of_player(currentLeftPlayer)

    print(f"[{session_id}] Start player: {db_getters.get_name_from_playerid(start_playerid)}")
    print(f"[{session_id}] End player: {db_getters.get_name_from_playerid(end_playerid)}")
    while not playerGuessed:
        # Wait for the frontend to POST a guess
        while "last_guess" not in game or game["last_guess"] is None:
            time.sleep(0.2)

        teammateGuess = game["last_guess"]
        game["last_guess"] = None  # consume

        if teammateGuess not in current_left_player_teammates:
            game["last_response"] = {"result": "not_a_teammate"}
            continue

        if locked_players.get(teammateGuess):
            game["last_response"] = {"result": "already_used"}
            continue

        over_limit = False
        relatedTeams = db_getters.get_common_teams(teammateGuess, currentLeftPlayer)
        for team in relatedTeams:
            guessed_teams[team] = guessed_teams.get(team, 0) + 1
            if guessed_teams[team] > TEAM_USE_LIMIT:
                over_limit = True
                break

        if over_limit:
            game["last_response"] = {"result": "over_limit"}
            continue

        # Valid guess!
        currentLeftPlayer = teammateGuess
        locked_players[currentLeftPlayer] = True
        current_left_player_teammates = db_getters.get_all_teammates_of_player(currentLeftPlayer)
        numGuesses += 1

        if teammateGuess == end_playerid:
            playerGuessed = True
            game["last_response"] = {
                "result": "correct",
                "guesses": numGuesses
            }
        else:
            game["last_response"] = {
                "result": "continue",
                "next_player": currentLeftPlayer,
                "next_player_name": db_getters.get_name_from_playerid(currentLeftPlayer),
                "teams": relatedTeams,
                "guesses": numGuesses
            }

    # Game is complete — wait for play-again signal from frontend
    while "play_again" not in game:
        time.sleep(0.2)

    if game["play_again"]:
        print(f"[{session_id}] Restarting game...")
        sessions.pop(session_id, None)
        # Start fresh game in same session
        start_game(StartRequest(session_id=session_id))
        single_player_connect_game(session_id)
    else:
        print(f"[{session_id}] Player exited.")
        sessions.pop(session_id, None)


def run():
    game_type = input("Which game would you like to play?\n - single\n - battle\n")
    if game_type.lower() == GameType.SINGLE.name.lower():
        single_player_connect_game(None)
    elif game_type.lower() == GameType.BATTLE.name.lower():
        battle_game(None)
        run()
    else:
        print("Bad input! Try again.\n")
        run()

if __name__ == "__main__":
    run()