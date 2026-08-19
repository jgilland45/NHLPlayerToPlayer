# This file holds static values, including the API and database endpoints, and other information.

# Generic endpoints for large data pulls (all games, all players, etc.)
import enum


ALL_GAMES_ENDPOINT = "https://api.nhle.com/stats/rest/en/game"
ALL_PLAYERS_ENDPOINT = "https://search.d3.nhle.com/api/v1/search/player?culture=en-us&limit=50000&q=*"

# Specific endpoints for individual data pulls (specific game, specific player, etc.)
SPECIFIC_GAME_ENDPOINT = "https://api-web.nhle.com/v1/gamecenter/{game_id}/boxscore"
SPECIFIC_PLAYER_ENDPOINT = "https://api-web.nhle.com/v1/player/{player_id}/landing"

# https://github.com/Zmalski/NHL-API-Reference/issues/23
# 1 - pre-season (1,998 games)
# 2 - regular season (63,930) including the entire 2024-2025 season, most of which haven't been played as of this post
# 3 - playoffs (5,017)
# 4 - all-star (84)
# 6 - World Cup group stage (36)
# 7 - World Cup knockout stage (18)
# 8 - World Cup pre-tournament (12)
# 9 - Olympics (168)
# 10 - Young Stars (2)
# 12 - Canadian All-Stars vs. American All-Stars (1) and Team King vs. Team Kloss (1) -> 2 total
# 13 - games lost to the 2004 labor dispute (1,230)
# 14 - Canada Cup (93)
# 18 - appears to be exhibition games played overseas (36) and not official regular season or playoff games
# 19 - Four Nations Face-off (6) -> played in lieu of the All-Star game in February, 2025
class GameType(enum.Enum):
    PRESEASON = 1
    REGULAR_SEASON = 2
    PLAYOFFS = 3
    ALL_STAR = 4
    WORLD_CUP_GROUP_STAGE = 6
    WORLD_CUP_KNOCKOUT_STAGE = 7
    WORLD_CUP_PRE_TOURNAMENT = 8
    OLYMPICS = 9
    YOUNG_STARS = 10
    CANADIAN_ALL_STARS_VS_AMERICAN_ALL_STARS = 12
    GAMES_LOST_TO_2004_LABOR_DISPUTE = 13
    CANADA_CUP = 14
    EXHIBITION_GAMES_PLAYED_OVERSEAS = 18
    FOUR_NATIONS_FACE_OFF = 19

    # converts to leading-zero string for use in API calls, e.g. 1 -> "01", 2 -> "02", etc.
    def formatted(self) -> str:
        return f"{self.value:02d}"