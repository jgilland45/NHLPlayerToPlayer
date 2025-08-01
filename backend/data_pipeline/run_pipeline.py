import asyncio
import httpx
from backend.db import crud, session
from backend.data_pipeline import sources
from backend.core.config import settings

async def main():
    """
    Main function to run the data pipeline.
    """
    # Get a database session
    # db = session.SessionLocal()

    # Get all seasons to process using the new helper function.
    # The start_season is now controlled by the config.

    # seasons_to_process = await sources.get_all_seasons(start_season=settings.PIPELINE_START_SEASON)
    seasons_to_process = [2024]

    async with httpx.AsyncClient() as client:
        for season in seasons_to_process:
            print(f"--- Processing season {season}-{season+1} ---")
            # Fetch all game IDs for the current season
            game_ids = await sources.get_all_game_ids_for_season(client, season)
            print(game_ids[:10])

            for game_id in game_ids:
                # Fetch the boxscore for the game
                game_data = await sources.fetch_game_boxscore(client, game_id)

                if game_data:
                    # Insert player data from the boxscore
                    # crud.bulk_insert_players_from_game_data(db, game_data)
                    players_in_game = await sources.get_players_in_game(client, game_id)
                    print(f"Processed game {game_id} for season {season}: {len(players_in_game)} players, {players_in_game[:5]}")

    # db.close()

if __name__ == "__main__":
    asyncio.run(main())