import httpx
import logging
from typing import List, Dict, Any

# Base URL for the new NHL API
NHL_API_BASE_URL = "https://api-web.nhle.com/v1"
NHL_API_BASE_URL_2 = "https://api.nhle.com/stats/rest/en"

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
            print(f"Game {game_id} not found (404), skipping.")
        else:
            print(f"HTTP error fetching game {game_id}: {e.response.status_code} - {e.response.text}")
    except httpx.RequestError as e:
        print(f"Request error for game {game_id}: {e}")
    return {}

async def fetch_player_landing(client: httpx.AsyncClient, player_id: int) -> Dict[str, Any]:
    """Fetches the landing page data for a single player to get their full name."""
    url = f"{NHL_API_BASE_URL}/player/{player_id}/landing"
    try:
        response = await client.get(url, timeout=10.0)
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            print(f"Player {player_id} not found (404).")
        else:
            print(f"HTTP error fetching player {player_id}: {e.response.status_code} - {e.response.text}")
    except httpx.RequestError as e:
        print(f"Request error for player {player_id}: {e}")
    return {}

async def get_all_game_ids_for_season(client: httpx.AsyncClient, season: int) -> List[int]:
    """Gets all game IDs for a given season."""
    print(f"Fetching all game IDs for {season}-{season+1} season.")
    # The API expects the season in YYYYYYYY format, e.g., 20232024
    season_str = f"{season}{season+1}"
    url = f"{NHL_API_BASE_URL_2}/game?cayenneExp=season={season_str}"
    try:
        response = await client.get(url, timeout=10.0)
        response.raise_for_status()
        all_games: List = response.json()['data']
        return [game['id'] for game in all_games]
    except httpx.HTTPStatusError as e:
        print(f"HTTP error fetching all games: {e.response.status_code} - {e.response.text}")
    return []
