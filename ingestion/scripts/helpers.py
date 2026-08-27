import logging
import asyncio
import httpx

from getters import get_all_games, get_specific_game
from transformers import transform_game_long_to_game_storage_list
from datatypes import DBGame, GameLong, GameStorage

logger = logging.getLogger(__name__)

async def test_for_season_202526():
    """
    Test the data ingestion for the 2025-26 season.
    """
    limits = httpx.Limits(max_connections=20)
    timeout = httpx.Timeout(30.0)
    async with httpx.AsyncClient(limits=limits, timeout=timeout) as client:
        games_db: list[DBGame] = await get_all_games(client)

        # Filter games for the 2025-26 season
        games_db_202526: list[DBGame] = [game for game in games_db if game.season == 20252026 or game.season == 19171918]

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

    # Transform the games to the format needed for the database
    game_storage_list: list[GameStorage] = []
    for game in games_long_202526:
        game_storage_list.extend(transform_game_long_to_game_storage_list(game))

    # Print important information to file to show this worked
    with open("test_for_season_202526_output.txt", "w") as f:
        f.write(f"Number of games for 2025-26 season: {len(games_db_202526)}\n")
        f.write(f"Number of GameLong objects for 2025-26 season: {len(games_long_202526)}\n")
        f.write(f"Number of GameStorage objects for 2025-26 season: {len(game_storage_list)}\n")
        f.write("\nSample GameStorage objects:\n")
        for game_storage in game_storage_list[:10]:  # Print first 10 for brevity
            f.write(f"{game_storage}\n")

    return game_storage_list