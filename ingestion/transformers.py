# This file is for any data transformation that needs to be done before setting data into databases (both postgres and neo4j).
# This should only include functions that are used to transform data.
# This includes data cleaning from the API sources, or transforming from SQL tables to graph nodes and edges.

import datatypes

def transform_game_long_to_game_storage(game: datatypes.GameLong) -> datatypes.GameStorage:
    """
    Transform a GameLong object to a GameStorage object.
    """
    pass
    # return datatypes.GameStorage(
    #     gameId=game.id,
    #     season=game.season,
    #     playerId=game.playerId,
    #     gameType=game.gameType,
    #     teamId=game.teamId
    # )

def transform_game_players_to_teammate_relationships(game: list[datatypes.GameStorage]) -> list[datatypes.TeammateRelationship]:
    """
    Transform a list of GameStorage objects to a list of TeammateRelationship objects.
    """
    relationships = []
    pass