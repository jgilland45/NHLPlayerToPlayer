import logging
import asyncio
import httpx

from datatypes import DBGame, DBPlayer, DBTeams, GameLong, GameStorage, TeamAPI
from getters import get_all_games, get_all_players, get_all_NHL_teams, get_specific_game
from transformers import transform_game_long_to_game_storage_list, transform_game_long_to_team_api, transform_team_api_to_db_teams
from setters import save_teams_to_postgres, save_games_to_postgres, save_players_to_postgres, save_game_players_to_postgres
from connection import connect_to_postgres, close_postgres_connection

logger = logging.getLogger(__name__)

async def test_for_season_202526():
    """
    Test the data ingestion for the 2025-26 season.
    """
    limits = httpx.Limits(max_connections=20)
    timeout = httpx.Timeout(30.0)
    async with httpx.AsyncClient(limits=limits, timeout=timeout) as client:
        games_db: list[DBGame] = await get_all_games(client)
        players_db: list[DBPlayer] = await get_all_players(client)

        # Filter games for the 2025-26 season
        games_db_202526: list[DBGame] = [game for game in games_db if game.season == 20252026]

        # Assert that there are games for the 2025-26 season
        assert len(games_db_202526) > 0, "No games found for the 2025-26 season. Please check the API or the data ingestion process."

        # Get GameLong objects for the 2025-26 season asynchronously
        async with asyncio.TaskGroup() as tg:
            tasks = [tg.create_task(get_specific_game(client, game.id)) for game in games_db_202526]

        games_long_202526: list[GameLong] = []
        for task in tasks:
            game = task.result()
            if game is not None:
                games_long_202526.append(game)

        # Get all teams
        # Get NHL teams
        nhl_teams_api: list[TeamAPI] = await get_all_NHL_teams(client)
    # Get additional teams that are not in the NHL (Olympics, all-star, etc.)
    non_nhl_teams_api: list[TeamAPI] = []
    for game in games_long_202526:
        non_nhl_teams_api.extend(transform_game_long_to_team_api(game))
    # Combine the two lists of teams and transform them to DBTeams (deduplicate teams)
    teams_api_by_id: dict[int, TeamAPI] = {}
    for team in nhl_teams_api + non_nhl_teams_api:
        teams_api_by_id.setdefault(team.id, team)
    teams_api: list[TeamAPI] = list(teams_api_by_id.values())
    teams_db: list[DBTeams] = [transform_team_api_to_db_teams(team) for team in teams_api]

    # Transform the games to the format needed for the database
    game_storage_list: list[GameStorage] = []
    for game in games_long_202526:
        game_storage_list.extend(transform_game_long_to_game_storage_list(game))

    # Save information to postgres
    connection = connect_to_postgres()
    if connection is None:
        logger.error("Failed to connect to PostgreSQL. Exiting the test.")
        return
    save_teams_to_postgres(connection, teams_db)
    save_games_to_postgres(connection, games_db_202526)
    save_players_to_postgres(connection, players_db)
    save_game_players_to_postgres(connection, game_storage_list)

    close_postgres_connection(connection)

    return game_storage_list