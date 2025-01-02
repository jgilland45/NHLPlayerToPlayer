import create_tables
import db_getters

def makeTeammateGuess(currentLeftPlayer):
    guessPlayer = input("Name a teammate of " + db_getters.get_name_from_playerid(currentLeftPlayer) + ": ")
    found_players = db_getters.get_playerids_from_name(guessPlayer)
    while (len(found_players) == 0):
        guessPlayer = input("Not found in database! Name a teammate: ")
        found_players = db_getters.get_playerids_from_name(guessPlayer)
    if (len(found_players) > 1):
        clarifyString = "Which one? Please type the number.\n"
        for index, playerid in enumerate(found_players):
            clarifyString = clarifyString + str(index) + " " + str(playerid) + "\n"
        clarifyIndex = input(clarifyString)
        while ((not clarifyIndex.isdigit()) or (int(clarifyIndex) >= len(found_players))):
            clarifyIndex = input("Please try again: " + clarifyString)
        clarifyIndex = int(clarifyIndex)
        found_player = found_players[clarifyIndex]
    else:
        found_player = found_players[0]
    return found_player

def run():
    print("Welcome! You will be trying to connect two NHL players.\n")
    dbpath = "testdb.db"
    create_tables.connect(dbpath)

    # start_playerid = db_getters.get_random_playerid()
    # end_playerid = db_getters.get_random_playerid()
    guessed_teams = {}
    locked_players = {}
    TEAM_USE_LIMIT = 3
    start_playerid = db_getters.get_random_playerid_from_team_and_years("edm", 20152016, 20242025)
    end_playerid = db_getters.get_random_playerid_from_team_and_years("edm", 20152016, 20242025)
    while (start_playerid == end_playerid):
        end_playerid = db_getters.get_random_playerid_from_team_and_years("edm", 20152016, 20242025)
    print("Start player: " + db_getters.get_name_from_playerid(start_playerid))
    print("End player: " + db_getters.get_name_from_playerid(end_playerid))
    playerGuessed = False
    numGuesses = 0
    currentLeftPlayer = start_playerid
    locked_players[currentLeftPlayer] = 1
    current_left_player_teammates = db_getters.get_all_teammates_of_player(currentLeftPlayer)
    while (not playerGuessed):
        teammateGuess = makeTeammateGuess(currentLeftPlayer)
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
        run()

if __name__ == "__main__":
    run()