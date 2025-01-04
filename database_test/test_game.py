import create_tables
import db_getters
from enum import Enum

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


TEAM_USE_LIMIT = 3

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

def battle_turn_options(current_left_player_teammates, current_left_player, locked_players, guessed_teams, player):
    turn_text = f"""
    Please type a teammate of {db_getters.get_name_from_playerid(current_left_player)} OR use one of the following powerups: {'time ' if player.get_time() else ''}{'list ' if player.get_listteam() else ''}{'skip ' if player.get_skip() else ''}
    """
    choice = input(turn_text)
    if choice.lower() == 'time':
        player.use_time()
        print("DOING TIME EXTEND")
        current_left_player, current_left_player_teammates = battle_turn_options(current_left_player_teammates, current_left_player, locked_players, guessed_teams, player)
        return current_left_player, current_left_player_teammates
    elif choice.lower() == 'list':
        player.use_listteam()
        teams_of_player = db_getters.get_teams_from_playerid(current_left_player)
        print(f"{db_getters.get_name_from_playerid(current_left_player)} has played for the following teams: {teams_of_player}\n")
        current_left_player, current_left_player_teammates = battle_turn_options(current_left_player_teammates, current_left_player, locked_players, guessed_teams, player)
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
            current_left_player, current_left_player_teammates = battle_turn_options(current_left_player_teammates, current_left_player, locked_players, guessed_teams, player)
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
    both_alive = True
    current_left_player = start_playerid
    locked_players[current_left_player] = 1
    current_left_player_teammates = db_getters.get_all_teammates_of_player(current_left_player)
    while both_alive:
        print(f"Player {'1' if player1_turn else '2'}'s turn.\n")
        current_left_player, current_left_player_teammates = battle_turn_options(current_left_player_teammates, current_left_player, locked_players, guessed_teams, player1 if player1_turn else player2)
        player1_turn = not player1_turn

def single_player_connect_game(settings):
    print("Welcome! You will be trying to connect two NHL players.\n")
    dbpath = "testdb.db"
    create_tables.connect(dbpath)
    # start_playerid = db_getters.get_random_playerid()
    # end_playerid = db_getters.get_random_playerid()
    guessed_teams = {}
    locked_players = {}
    start_playerid = db_getters.get_random_playerid_from_years(20152016, 20242025)
    end_playerid = db_getters.get_random_playerid_from_years(20152016, 20242025)
    while (start_playerid == end_playerid):
        end_playerid = db_getters.get_random_playerid_from_years(20152016, 20242025)
    print("Start player: " + db_getters.get_name_from_playerid(start_playerid))
    print("End player: " + db_getters.get_name_from_playerid(end_playerid))
    playerGuessed = False
    numGuesses = 0
    currentLeftPlayer = start_playerid
    locked_players[currentLeftPlayer] = 1
    current_left_player_teammates = db_getters.get_all_teammates_of_player(currentLeftPlayer)
    while (not playerGuessed):
        teammateGuess = make_teammate_guess(currentLeftPlayer)
        if (teammateGuess in current_left_player_teammates):
            try:
                if locked_players[teammateGuess]:
                    print(f"Cannot use {db_getters.get_name_from_playerid(teammateGuess)} since they were already used")
                    continue
            except:
                pass
            over_limit = False
            relatedTeams = db_getters.get_common_teams(teammateGuess, currentLeftPlayer)
            for relatedTeam in relatedTeams:
                try:
                    guessed_teams[relatedTeam]+=1
                except:
                    guessed_teams[relatedTeam] = 1
                if guessed_teams[relatedTeam] > TEAM_USE_LIMIT:
                    print(f"Cannot use this player - over team limit for team {relatedTeam}")
                    over_limit = True
                    break
            if over_limit:
                continue
            print("Yes! They both played for:")
            for relatedTeam in relatedTeams:
                print(relatedTeam)
            if (teammateGuess == end_playerid):
                playerGuessed = True
            else:
                currentLeftPlayer = teammateGuess
                locked_players[currentLeftPlayer] = 1
                current_left_player_teammates = db_getters.get_all_teammates_of_player(currentLeftPlayer)
            numGuesses+=1
        else:
            print("Not a teammate! Guess again!")
    print("You got there in " + str(numGuesses) + " players!")
    playAgain = input("Type 'exit' to stop playing, and type anything else to play again.\n")
    if (playAgain.lower() != "exit"):
        single_player_connect_game(None)


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