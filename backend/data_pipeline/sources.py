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

async def get_all_game_ids_for_season(client: httpx.AsyncClient, season: int) -> List[int]:
    """Gets all game IDs for a given season."""
    print(f"Fetching all game IDs for {season}-{season+1} season.")
    url = f"{NHL_API_BASE_URL_2}/game"
    try:
        response = await client.get(url, timeout=10.0)
        response.raise_for_status()
        all_games: List = response.json()['data']
        print(list(map(lambda x: x['id'], all_games))[-10:])
        # Filter games by season and extract game IDs
        # The game ID format is YYYY02XXXX for regular season, YYYY03XXXX for playoffs, and similar for other game types
        # We want to ensure we only get games for the specified season.
        return [game['id'] for game in all_games if game['id'] > season * 1000000 + 20000 and game['id'] < season * 1000000 + 99999]
    except httpx.HTTPStatusError as e:
        print(f"HTTP error fetching all games: {e.response.status_code} - {e.response.text}")
    return []

async def get_players_in_game(client: httpx.AsyncClient, gameid: int) -> List[Dict[str, Any]]:
    game_url = f"{NHL_API_BASE_URL}/gamecenter/{gameid}/boxscore"

    try:
        response = await client.get(game_url, timeout=10.0)
        response.raise_for_status()
        data = response.json()
        home_team = data['playerByGameStats']['homeTeam']
        home_team_tricode = data['homeTeam']['abbrev']
        away_team = data['playerByGameStats']['awayTeam']
        away_team_tricode = data['awayTeam']['abbrev']
        season = data['season']
        positions = ['forwards', 'defense', 'goalies']
        player_game_info = []
        for position in positions:
            players = home_team[position]
            for player in players:
                player_game_info.append({
                    'playerid': player['playerId'],
                    'gameid': gameid,
                    'teamid': home_team_tricode + str(season),
                    })
            players = away_team[position]
            for player in players:
                player_game_info.append({
                    'playerid': player['playerId'],
                    'gameid': gameid,
                    'teamid': away_team_tricode + str(season),
                    })
        return player_game_info
    except httpx.HTTPStatusError as e:
        print(f"HTTP error fetching players in game: {e.response.status_code} - {e.response.text}")
        
    return []
