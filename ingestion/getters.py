# This file is for getting data from various sources (both APIs and databases).
# This should only include functions that are used to get data. No data transformation should be done here.

import logging
from typing import Optional
import httpx
import psycopg2

import statics
import datatypes

logger = logging.getLogger(__name__)

# API getters

async def _get(client: httpx.AsyncClient, endpoint: str) -> httpx.Response:
    try:
        response = await client.get(endpoint)
    except httpx.RequestError as error:
        raise RuntimeError(f"Request to NHL API failed: {endpoint}") from error

    response.raise_for_status()
    return response

async def get_all_games(client: httpx.AsyncClient) -> list[datatypes.DBGame]:
    """
    Get all games from the NHL API.
    """
    logger.debug("Requesting all games from %s", statics.ALL_GAMES_ENDPOINT)
    response = await _get(client, statics.ALL_GAMES_ENDPOINT)
    data = response.json()["data"]

    games = [datatypes.DBGame(**game) for game in data]
    logger.info("Fetched %d games", len(games))
    return games

async def get_all_players(client: httpx.AsyncClient) -> list[datatypes.DBPlayer]:
    """
    Get all players from the NHL API.
    """
    response = await _get(client, statics.ALL_PLAYERS_ENDPOINT)
    return [datatypes.DBPlayer(**player) for player in response.json()]

async def get_specific_game(client: httpx.AsyncClient, game_id: int) -> Optional[datatypes.GameLong]:
    """
    Get a specific game from the NHL API.
    """
    endpoint = statics.SPECIFIC_GAME_ENDPOINT.format(game_id=game_id)
    logger.debug("Requesting game %d from %s", game_id, endpoint)
    try:
        response = await client.get(endpoint)
    except httpx.RequestError as error:
        raise RuntimeError(f"Request for game {game_id} failed") from error

    if response.status_code == 404:
        logger.warning("Game %d was not found (404); skipping", game_id)
        return None
    response.raise_for_status()

    try:
        game = datatypes.dataclass_from_dict(response.json(), datatypes.GameLong)
    except (KeyError, TypeError, ValueError) as error:
        raise ValueError(f"Failed to parse response for game {game_id}: {error}") from error
    logger.info("Fetched game %d", game_id)
    return game

async def get_specific_player(client: httpx.AsyncClient, player_id: int) -> datatypes.PlayerLong:
    """
    Get a specific player from the NHL API.
    """
    endpoint = statics.SPECIFIC_PLAYER_ENDPOINT.format(player_id=player_id)
    response = await _get(client, endpoint)
    return datatypes.PlayerLong(**response.json())

async def get_all_NHL_teams(client: httpx.AsyncClient) -> list[datatypes.TeamAPI]:
    """
    Get all teams from the NHL API.
    """
    response = await _get(client, statics.ALL_NHL_TEAMS_ENDPOINT)
    return [datatypes.TeamAPI(**team) for team in response.json()["data"]]

# Database getters

def get_game_storage_by_filters_from_db(
        connection: psycopg2.extensions.connection,
        filters: datatypes.OptionalGameStorage
    ) -> list[datatypes.GameStorage]:
    """
    Get game storage from the database based on filters.
    """
    conditions: list[str] = []

    if filters.season is not None:
        conditions.append("season = %s")
    if filters.gameId is not None:
        conditions.append("game_id = %s")
    if filters.playerId is not None:
        conditions.append("player_id = %s")
    if filters.teamId is not None:
        conditions.append("team_id = %s")
    if filters.gameType is not None:
        conditions.append("game_type = %s")

    parameters = [
        value
        for value in (
            filters.season,
            filters.gameId,
            filters.playerId,
            filters.teamId,
            getattr(filters.gameType, "value", filters.gameType),
        )
        if value is not None
    ]

    where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
    query = f"""
        SELECT game_id, season, player_id, team_id, game_type
        FROM game_players
        {where_clause};
    """

    with connection.cursor() as cursor:
        cursor.execute(query, parameters)
        rows = cursor.fetchall()

    game_storage_list: list[datatypes.GameStorage] = []
    for row in rows:
        game_storage_list.append(datatypes.GameStorage(
            gameId=row[0],
            season=row[1],
            playerId=row[2],
            teamId=row[3],
            gameType=statics.GameType(row[4])
        ))
    logger.info(
        "Fetched %d game storage records from database with filters: %s",
        len(game_storage_list),
        filters
    )
    return game_storage_list