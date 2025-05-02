import create_tables
import db_getters
from enum import Enum
import time
from pydantic import BaseModel
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from collections import deque, defaultdict
import threading

# run using: `uvicorn test_game:app --reload --host 0.0.0.0 --port 8080`

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def build_teammate_graph():
    global teammate_graph, graph_building_status
    graph_building_status["status"] = "building"

    print("Building in-memory teammate graph...")
    create_tables.connect(DB_PATH)

    create_tables.cursor.execute("""
        SELECT playerid, gameid, teamid FROM Player_Game
    """)
    rows = create_tables.cursor.fetchall()

    grouped = defaultdict(list)
    for pid, gid, tid in rows:
        grouped[(gid, tid)].append(pid)

    graph = defaultdict(set)
    for players in grouped.values():
        for p1 in players:
            for p2 in players:
                if p1 != p2:
                    graph[p1].add(p2)

    teammate_graph = graph
    graph_building_status["status"] = "ready"
    print(f"Graph loaded with {len(graph)} players.")


# Global state (for simplicity)
TEAM_USE_LIMIT = 3
DB_PATH = "testdb.db"
sessions = {}
clients = []
teammate_graph = {}
graph_building_status = {"status": "building"}

class GuessRequest(BaseModel):
    session_id: str
    guess: int

class JoinLobbyRequest(BaseModel):
    client: str

class StartRequest(BaseModel):
    session_id: str

class PlayAgainRequest(BaseModel):
    session_id: str
    play_again: bool
    

class GameType(str, Enum):
    SINGLE = 'single-player'
    MULTI = 'multi-player'
    BATTLE = 'battle'

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
    
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()
    
@app.websocket("/ws/{client}")
async def websocket_endpoint(websocket: WebSocket, client: str):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(f"You wrote: {data}", websocket)
            await manager.broadcast(f"Client #{client} says: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{client} left the chat")
    
@app.post("/multi-player/join-lobby")
def join_lobby(req: JoinLobbyRequest):
    clients.append(req.client)
    return {"status": "lobby_joined"}
    
@app.post("/{game_type}/start-game")
def start_game(req: StartRequest, game_type: GameType):
    """
    Initializes a new game and stores session state.
    """
    session_id = req.session_id
    create_tables.connect(DB_PATH)

    start_id = db_getters.get_random_playerid_from_years(20152016, 20242025)
    if (game_type is GameType.SINGLE):
        end_id = db_getters.get_random_playerid_from_years(20152016, 20242025)
        while end_id == start_id:
            end_id = db_getters.get_random_playerid_from_years(20152016, 20242025)
    else:
        end_id = 0
    # start_id = db_getters.get_random_playerid()
    # end_id = db_getters.get_random_playerid()
    # while end_id == start_id:
    #     end_id = db_getters.get_random_playerid()

    condition = threading.Condition()

    sessions[session_id] = {
        "start": start_id,
        "end": end_id,
        "current": start_id,
        "locked": {start_id: True},
        "guessed_teams": {},
        "guesses": 0,
        "last_guess": None,
        "last_response": None,
        "play_again": None,
        "condition": condition,
    }

    # Start the backend game loop in a separate thread
    if (game_type is GameType.SINGLE):
        threading.Thread(target=single_player_connect_game, args=(session_id,), daemon=True).start()
    elif (game_type is GameType.MULTI):
        threading.Thread(target=battle_game, args=(session_id,clients,), daemon=True).start()

    return {
        "start_player": start_id,
        "end_player": end_id,
    }

@app.post("/{game_type}/make-guess")
def make_guess(req: GuessRequest):
    """
    Processes a single teammate guess for the given session.
    """
    session = sessions.get(req.session_id)
    if not session:
        return {"error": "Session not found"}

    print(f"Received guess playerid: {req.guess}")
    session["last_guess"] = req.guess
    with session["condition"]:
        session["condition"].notify()

    return {"status": "guess_received"}

@app.get("/{game_type}/check-response")
def check_response(session_id: str):
    session = sessions.get(session_id)
    if not session:
        return {"error": "Session not found"}

    if session["last_response"] is not None:
        response = session["last_response"]
        session["last_response"] = None  # Clear it
        return response

    return {"result": "waiting"}

@app.get("/multi-player/check-state")
def check_state(session_id: str):
    session = sessions.get(session_id)
    if not session:
        return {"error": "Session not found"}

    if session["turn"] is not None:
        return {
            "result": session["turn"],
            "data": check_response(session_id),
        }

    return {"result": "waiting"}

@app.post("/{game_type}/play-again")
def play_again(req: PlayAgainRequest, game_type: GameType):
    session = sessions.get(req.session_id)
    if not session:
        return {"error": "Session not found"}

    # Remove old session and thread state
    sessions.pop(req.session_id, None)

    # Start a new game (reusing the /start-game logic)
    return start_game(StartRequest(session_id=req.session_id), game_type)

@app.get("/{game_type}/graph-status")
def graph_status():
    return graph_building_status

@app.get("/{game_type}/shortest-path")
def get_shortest_path(player1: int, player2: int):
    return shortest_path(player1, player2)

def get_all_teammates_of_player(playerid):
    global teammate_graph
    return list(teammate_graph.get(playerid, []))

def shortest_path(player1, player2):
    global teammate_graph
    visited = set()
    queue = deque([(player1, [player1])])

    while queue:
        current, path = queue.popleft()
        if current == player2:
            return {"path": path}
        for neighbor in teammate_graph.get(current, []):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))
    return {"path": []}

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
        current_left_player_teammates = get_all_teammates_of_player(currentLeftPlayer)
        return currentLeftPlayer, current_left_player_teammates

def battle_game(session_id: str, clients: list[str]):
    global teammate_graph
    # Wait for graph to finish building
    while graph_building_status["status"] != "ready":
        time.sleep(0.1)
    print(f"[{session_id}] Starting multi player game...")
    create_tables.connect(DB_PATH)

    game = sessions.get(session_id)
    if not game:
        print(f"[{session_id}] Session not found.")
        return
    start_playerid = game["start"]

    print(f"[{session_id}] Start player: {db_getters.get_name_from_playerid(start_playerid)}")
    # player1 = Player()
    # player2 = Player()
    current_left_player = start_playerid
    locked_players = {current_left_player: True}
    guessed_teams = {}
    teams_over_limit = []
    current_left_player_teammates = get_all_teammates_of_player(current_left_player)
    current_client_idx = 0
    game["turn"] = clients[current_client_idx]
    game["last_response"] = {
        "start_player": start_playerid,
    }
    num_guesses = 0
    # while True:
    #     print(f"Player {'1' if player1_turn else '2'}'s turn.\n")
    #     current_left_player, current_left_player_teammates = battle_turn_options(current_left_player_teammates, current_left_player, locked_players, guessed_teams, player1 if player1_turn else player2, time.time(), 20)
    #     if current_left_player == -1:
    #         print(f"Player {'1' if player1_turn else '2'} ran out of time. Player {'2' if player1_turn else '1'} wins!!")
    #         break
    #     player1_turn = not player1_turn

    while True:
        with game["condition"]:
            while game["last_guess"] is None:
                game["condition"].wait()
        print(f"Current player's turn: {game['turn']}")
        teammate_guess = game["last_guess"]
        game["last_guess"] = None

        if teammate_guess not in current_left_player_teammates:
            game["last_response"] = {
                "result": "not_a_teammate",
                "player": teammate_guess,
            }
            continue

        if locked_players.get(teammate_guess):
            game["last_response"] = {
                "result": "already_used",
            }
            continue

        teams = db_getters.get_common_teams(teammate_guess, current_left_player)
        over_limit = False
        for team in teams:
            guessed_teams[team] = guessed_teams.get(team, 0) + 1
            if guessed_teams[team] > TEAM_USE_LIMIT:
                over_limit = True
                teams_over_limit.append(team)

        if over_limit:
            game["last_response"] = {
                "result": "over_limit",
                "teams": teams_over_limit
            }
            teams_over_limit.clear()
            continue

        # Valid guess
        current_left_player = teammate_guess
        locked_players[current_left_player] = True
        guessed_team_strikes = list(map(lambda t: guessed_teams.get(t, 0), teams))
        num_guesses+=1

        game["current"] = current_left_player
        game["guesses"] = num_guesses

        # TODO: find good end condition (maybe timer?)
        game["last_response"] = {
            "result": "continue",
            "next_player": current_left_player,
            "teams": teams,
            "strikes": guessed_team_strikes,
            "guesses": num_guesses
        }

        current_left_player_teammates = get_all_teammates_of_player(current_left_player)
        # move to next player
        current_client_idx = (current_client_idx + 1) % len(clients)
        game["turn"] = clients[current_client_idx]

    # Game over – wait for restart or exit
    with game["condition"]:
        while game["play_again"] is None:
            game["condition"].wait()

    # Exit cleanly. The new thread will be started by /play-again
    sessions.pop(session_id, None)

def single_player_connect_game(session_id: str):
    global teammate_graph
    # Wait for graph to finish building
    while graph_building_status["status"] != "ready":
        time.sleep(0.1)
    print(f"[{session_id}] Starting single player game...")
    create_tables.connect(DB_PATH)

    game = sessions.get(session_id)
    if not game:
        print(f"[{session_id}] Session not found.")
        return
    start_playerid = game["start"]
    end_playerid = game["end"]
    current_left_player = start_playerid
    num_guesses = 0
    locked_players = {current_left_player: True}
    guessed_teams = {}
    teams_over_limit = []
    current_left_player_teammates = get_all_teammates_of_player(current_left_player)

    print(f"[{session_id}] Start player: {db_getters.get_name_from_playerid(start_playerid)}")
    print(f"[{session_id}] End player: {db_getters.get_name_from_playerid(end_playerid)}")
    while True:
        with game["condition"]:
            while game["last_guess"] is None:
                game["condition"].wait()
        num_guesses += 1
        teammate_guess = game["last_guess"]
        game["last_guess"] = None

        if teammate_guess not in current_left_player_teammates:
            game["last_response"] = {
                "result": "not_a_teammate",
                "player": teammate_guess,
            }
            continue

        if locked_players.get(teammate_guess):
            game["last_response"] = {"result": "already_used"}
            continue

        teams = db_getters.get_common_teams(teammate_guess, current_left_player)
        over_limit = False
        for team in teams:
            guessed_teams[team] = guessed_teams.get(team, 0) + 1
            if guessed_teams[team] > TEAM_USE_LIMIT:
                over_limit = True
                teams_over_limit.append(team)

        if over_limit:
            game["last_response"] = {
                "result": "over_limit",
                "teams": teams_over_limit
            }
            teams_over_limit.clear()
            continue

        # Valid guess
        current_left_player = teammate_guess
        locked_players[current_left_player] = True
        guessed_team_strikes = list(map(lambda t: guessed_teams.get(t, 0), teams))

        game["current"] = current_left_player
        game["guesses"] = num_guesses

        if current_left_player == end_playerid:
            game["last_response"] = {
                "result": "correct",
                "teams": teams,
                "strikes": guessed_team_strikes,
                "guesses": num_guesses
            }
            break
        else:
            game["last_response"] = {
                "result": "continue",
                "next_player": current_left_player,
                "teams": teams,
                "strikes": guessed_team_strikes,
                "guesses": num_guesses
            }

        current_left_player_teammates = get_all_teammates_of_player(current_left_player)

    # Game over – wait for restart or exit
    with game["condition"]:
        while game["play_again"] is None:
            game["condition"].wait()

    # Exit cleanly. The new thread will be started by /play-again
    sessions.pop(session_id, None)


# def run():
#     game_type = input("Which game would you like to play?\n - single\n - battle\n")
#     if game_type.lower() == GameType.SINGLE.name.lower():
#         single_player_connect_game(None)
#     elif game_type.lower() == GameType.BATTLE.name.lower():
#         battle_game(None)
#         run()
#     else:
#         print("Bad input! Try again.\n")
#         run()

# if __name__ == "__main__":
#     run()


# Build the graph at server start
threading.Thread(target=build_teammate_graph, daemon=True).start()