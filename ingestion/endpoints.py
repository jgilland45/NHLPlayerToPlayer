# This file holds the API and database endpoints.

# Generic endpoints for large data pulls (all games, all players, etc.)
ALL_GAMES_ENDPOINT = "https://api.nhle.com/stats/rest/en/game"
ALL_PLAYERS_ENDPOINT = "https://search.d3.nhle.com/api/v1/search/player?culture=en-us&limit=50000&q=*"

# Specific endpoints for individual data pulls (specific game, specific player, etc.)
SPECIFIC_GAME_ENDPOINT = "https://api-web.nhle.com/v1/gamecenter/{game_id}/boxscore"
SPECIFIC_PLAYER_ENDPOINT = "https://api-web.nhle.com/v1/player/{player_id}/landing"
