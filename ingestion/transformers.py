# This file is for any data transformation that needs to be done before setting data into databases (both postgres and neo4j).
# This should only include functions that are used to transform data.
# This includes data cleaning from the API sources, or transforming from SQL tables to graph nodes and edges.

import logging
import datatypes

logger = logging.getLogger(__name__)

def transform_game_long_to_game_storage_list(game: datatypes.GameLong) -> list[datatypes.GameStorage]:
    """
    Transform a GameLong object to a list of GameStorage objects.
    """
    game_id = game.id
    season = game.season
    game_type = game.gameType
    game_storage_list: list[datatypes.GameStorage] = []
    # Create GameStorage for home team
    team_id = game.homeTeam.id
    home_team_game_storage_list: list[datatypes.GameStorage] = []

    home_team_forwards = game.playerByGameStats.homeTeam.forwards
    home_team_defense = game.playerByGameStats.homeTeam.defense
    home_team_goalies = game.playerByGameStats.homeTeam.goalies

    for player in home_team_forwards + home_team_defense + home_team_goalies:
        home_team_game_storage_list.append(datatypes.GameStorage(
            gameId=game_id,
            season=season,
            playerId=player.playerId,
            gameType=game_type,
            teamId=team_id
        ))


    # Create GameStorage for away team
    team_id = game.awayTeam.id
    away_team_game_storage_list: list[datatypes.GameStorage] = []

    away_team_forwards = game.playerByGameStats.awayTeam.forwards
    away_team_defense = game.playerByGameStats.awayTeam.defense
    away_team_goalies = game.playerByGameStats.awayTeam.goalies

    for player in away_team_forwards + away_team_defense + away_team_goalies:
        away_team_game_storage_list.append(datatypes.GameStorage(
            gameId=game_id,
            season=season,
            playerId=player.playerId,
            gameType=game_type,
            teamId=team_id
        ))

    game_storage_list.extend(home_team_game_storage_list)
    game_storage_list.extend(away_team_game_storage_list)
    logger.info(
        "Transformed game %d into %d GameStorage objects",
        game_id,
        len(game_storage_list),
    )
    return game_storage_list

def transform_game_players_to_teammate_relationships(game: list[datatypes.GameStorage]) -> list[datatypes.TeammateRelationship]:
    """
    Transform a list of GameStorage objects to a list of TeammateRelationship objects.
    Assumptions:
    - All players in the list are from the same game.
    - Players are teammates if they are on the same team in the same game.
    - This list of GameStorage objects will be players from one of two teams in the game.
    """
    relationships: list[datatypes.TeammateRelationship] = []

    # Iterate through each player in the list and create a relationship with every other player on the same team
    for i in range(len(game)):
        for j in range(i + 1, len(game)):
            if game[i].teamId == game[j].teamId:
                relationships.append(datatypes.TeammateRelationship(
                    player1Id=game[i].playerId,
                    player2Id=game[j].playerId,
                    teamId=game[i].teamId,
                    season=game[i].season,
                    gameType=game[i].gameType
                ))

    return relationships

def transform_game_long_to_team_api(game: datatypes.GameLong) -> list[datatypes.TeamAPI]:
    """
    Transform a GameLong object to a list of TeamAPI objects.
    """
    team_api_list: list[datatypes.TeamAPI] = []
    team_api_list.append(datatypes.TeamAPI(
        id=game.homeTeam.id,
        fullName=game.homeTeam.commonName.default,
        leagueId=0,
        rawTricode=game.homeTeam.abbrev,
        triCode=game.homeTeam.abbrev,
        franchiseId=0
    ))
    team_api_list.append(datatypes.TeamAPI(
        id=game.awayTeam.id,
        fullName=game.awayTeam.commonName.default,
        leagueId=0,
        rawTricode=game.awayTeam.abbrev,
        triCode=game.awayTeam.abbrev,
        franchiseId=0
    ))
    return team_api_list

def transform_team_api_to_db_teams(team: datatypes.TeamAPI) -> datatypes.DBTeams:
    """
    Transform a TeamAPI object to a DBTeams object.
    """
    return datatypes.DBTeams(
        teamId=team.id,
        teamAbbrev=team.triCode,
        teamName=team.fullName
    )