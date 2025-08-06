import asyncio
import httpx
import logging
from functools import wraps
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

# Base URL for the new NHL API
NHL_API_BASE_URL = "https://api-web.nhle.com/v1"
NHL_API_BASE_URL_2 = "https://api.nhle.com/stats/rest/en"

def async_retry(max_retries=3, initial_delay=1.0, backoff=2.0):
    """
    A decorator for retrying an async function on transient network errors.
    It will retry on any httpx.RequestError (e.g., ReadError, ConnectError).
    If all retries fail, the original exception is re-raised to be handled
    by the function's own error handling.
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            delay = initial_delay
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except httpx.RequestError as e:
                    if attempt < max_retries - 1:
                        logger.warning(f"Attempt {attempt + 1}/{max_retries} failed for {func.__name__}: {type(e).__name__}. Retrying in {delay:.2f}s...")
                        await asyncio.sleep(delay)
                        delay *= backoff
                    else:
                        logger.error(f"Final attempt for {func.__name__} failed.", exc_info=True)
                        raise # On the final attempt, re-raise the exception.
        return wrapper
    return decorator

@async_retry()
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
            logger.debug(f"Game {game_id} not found (404), skipping.")
        else:
            logger.error(f"HTTP error fetching game {game_id}: {e.response.status_code} - {e.response.text}")
    except httpx.RequestError as e:
        logger.error(f"Request error for game {game_id}: {type(e).__name__} for URL {e.request.url}")
    return {}

@async_retry()
async def fetch_player_landing(client: httpx.AsyncClient, player_id: int) -> Dict[str, Any]:
    """Fetches the landing page data for a single player to get their full name."""
    url = f"{NHL_API_BASE_URL}/player/{player_id}/landing"
    try:
        response = await client.get(url, timeout=10.0)
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            logger.warning(f"Player {player_id} not found (404).")
        else:
            logger.error(f"HTTP error fetching player {player_id}: {e.response.status_code} - {e.response.text}")
    except httpx.RequestError as e:
        logger.error(f"Request error for player {player_id}: {type(e).__name__} for URL {e.request.url}")
    return {}

async def get_all_game_ids_for_season(client: httpx.AsyncClient, season: int) -> List[int]:
    """Gets all game IDs for a given season."""
    logger.info(f"Fetching all game IDs for {season}-{season+1} season.")
    # The API expects the season in YYYYYYYY format, e.g., 20232024
    season_str = f"{season}{season+1}"
    url = f"{NHL_API_BASE_URL_2}/game?cayenneExp=season={season_str}"
    try:
        response = await client.get(url, timeout=10.0)
        response.raise_for_status()
        all_games: List = response.json()['data']
        return [game['id'] for game in all_games]
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error fetching all games: {e.response.status_code} - {e.response.text}")
    return []
