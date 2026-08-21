# This file is for getting data from various sources (both APIs and databases).
# This should only include functions that are used to get data. No data transformation should be done here.

import requests

import statics
import datatypes

# API getters

def get_all_games() -> list[datatypes.GameShort]:
    """
    Get all games from the NHL API.
    """
    r = requests.get(statics.ALL_GAMES_ENDPOINT)
    if r.status_code != 200:
        raise Exception(f"Failed to get all games from NHL API. Status code: {r.status_code}")

    data = r.json()["data"]

    return [datatypes.GameShort(**game) for game in data]

def get_all_players() -> list[datatypes.PlayerShort]:
    """
    Get all players from the NHL API.
    """
    r = requests.get(statics.ALL_PLAYERS_ENDPOINT)
    if r.status_code != 200:
        raise Exception(f"Failed to get all players from NHL API. Status code: {r.status_code}")

    return [datatypes.PlayerShort(**player) for player in r.json()]

def get_specific_game(game_id: int) -> datatypes.GameLong:
    """
    Get a specific game from the NHL API.
    """
    r = requests.get(statics.SPECIFIC_GAME_ENDPOINT.format(game_id=game_id))
    if r.status_code != 200:
        raise Exception(f"Failed to get specific game from NHL API. Status code: {r.status_code}")

    return datatypes.GameLong(**r.json())

def get_specific_player(player_id: int) -> datatypes.PlayerLong:
    """
    Get a specific player from the NHL API.
    """
    r = requests.get(statics.SPECIFIC_PLAYER_ENDPOINT.format(player_id=player_id))
    if r.status_code != 200:
        raise Exception(f"Failed to get specific player from NHL API. Status code: {r.status_code}")

    return datatypes.PlayerLong(**r.json())

# Database getters

def get_all_games_from_postgres() -> list[datatypes.GameStorage]:
    """
    Get all games from the Postgres database.
    """
    # Implementation for fetching all games from the Postgres database
    pass

def get_specific_game_from_postgres(game_id: int) -> datatypes.GameStorage:
    """
    Get a specific game from the Postgres database.
    This gets all playerId-gameId pairs for a specific game, which is used to get all players that played in a specific game.
    """
    # Implementation for fetching a specific game from the Postgres database
    pass