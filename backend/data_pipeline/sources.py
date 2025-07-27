import httpx
import asyncio
import logging
from typing import List, Dict, Any
from datetime import datetime

# Use a logger for better debugging
logger = logging.getLogger(__name__)

# Base URL for the new NHL API
NHL_API_BASE_URL = "https://api-web.nhle.com/v1"

async def fetch_game_boxscore(client: httpx.AsyncClient, game_id: int) -> Dict[str, Any]:
    """Fetches the boxscore for a single game."""
    url = f"{NHL_API_BASE_URL}/gamecenter/{game_id}/boxscore"
    try:
        response = await client.get(url, timeout=10.0)
        response.raise_for_status()  # Raises an exception for 4xx/5xx status codes
        return response.json()
    except httpx.HTTPStatusError as e:
        # It's common for game IDs in a generated range not to exist (e.g. cancelled games).
        # We'll log 404s at a lower level to avoid noise, and other errors as actual errors.
        if e.response.status_code == 404:
            logger.info(f"Game {game_id} not found (404), skipping.")
        else:
            logger.error(f"HTTP error fetching game {game_id}: {e.response.status_code} - {e.response.text}")
    except httpx.RequestError as e:
        logger.error(f"Request error for game {game_id}: {e}")
    return {}

async def get_all_game_ids_for_season(season: int) -> List[int]:
    """Gets all game IDs for a given season."""
    # This endpoint needs to be found or built, assuming one exists.
    # For now, let's assume a placeholder.
    # In a real scenario, you might need to iterate through schedules.
    # Example: 'https://api.nhle.com/stats/rest/en/game?season=20232024'
    # The logic from your old scripts can be adapted here.
    logger.info(f"Fetching all game IDs for {season}-{season+1} season.")
    # This is a simplified placeholder.
    # You would adapt your existing logic for getting all games here.
    return list(range(2023020001, 2023021312 + 1)) # Example range for a full season
