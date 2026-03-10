import asyncio
import logging
import random
import secrets
import string
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Set

from backend.db import getters
from backend.game.connection_settings import (
    DEFAULT_RELATIONSHIP_TYPES,
    ResolvedConnectionSettings,
    get_connection_settings_options,
    resolve_connection_settings,
    serialize_resolved_connection_settings,
)

TURN_SECONDS = 20
TEAM_SEASON_CONNECTION_CAP = 3
LOBBY_CODE_LENGTH = 6
MAX_PLAYERS = 2
logger = logging.getLogger("uvicorn.error")


@dataclass
class MultiplayerSeat:
    name: str
    token: str
    joined_at: float


@dataclass
class MultiplayerRound:
    current_path: List[Dict[str, Any]]
    used_player_ids: Set[int]
    step_teams: List[List[str]]
    team_usage: Dict[str, int]
    active_player_token: str
    turn_started_at: float
    turn_deadline: float
    game_over: bool = False
    winner_token: Optional[str] = None
    loser_token: Optional[str] = None
    end_reason: Optional[str] = None


@dataclass
class MultiplayerLobby:
    code: str
    created_at: float
    creator_token: str
    connection_settings: ResolvedConnectionSettings
    players: List[MultiplayerSeat] = field(default_factory=list)
    round: Optional[MultiplayerRound] = None


class LobbyNotFoundError(ValueError):
    pass


class LobbyFullError(ValueError):
    pass


class DuplicateNameError(ValueError):
    pass


class InvalidTokenError(ValueError):
    pass


class InvalidActionError(ValueError):
    pass


class MultiplayerGameService:
    def __init__(self):
        self._lobbies: Dict[str, MultiplayerLobby] = {}
        self._lock = asyncio.Lock()

    def _generate_lobby_code(self) -> str:
        alphabet = string.ascii_uppercase + string.digits
        return "".join(secrets.choice(alphabet) for _ in range(LOBBY_CODE_LENGTH))

    async def get_settings_options(self) -> Dict[str, Any]:
        return await get_connection_settings_options(default_relationship_types=DEFAULT_RELATIONSHIP_TYPES)

    async def _get_lobby_default_settings(self) -> ResolvedConnectionSettings:
        fallback = ResolvedConnectionSettings(
            game_types=list(DEFAULT_RELATIONSHIP_TYPES),
            teams=[],
            start_year=1917,
            end_year=datetime.utcnow().year,
        )

        try:
            options = await asyncio.wait_for(
                get_connection_settings_options(default_relationship_types=DEFAULT_RELATIONSHIP_TYPES),
                timeout=3.0,
            )
        except asyncio.TimeoutError:
            logger.warning("Timed out loading multiplayer settings options during lobby creation; using fallback defaults")
            return fallback
        except Exception:
            logger.exception("Failed loading multiplayer settings options during lobby creation; using fallback defaults")
            return fallback

        game_type_ids = [
            entry["id"]
            for entry in options.get("game_types", [])
            if isinstance(entry, dict) and isinstance(entry.get("id"), str) and entry["id"]
        ]
        if not game_type_ids:
            return fallback

        allowed_teams = [team for team in options.get("teams", []) if isinstance(team, str) and team.strip()]
        defaults = options.get("defaults", {})

        game_type_set = set(game_type_ids)
        selected_game_types = [
            game_type
            for game_type in defaults.get("game_types", [])
            if isinstance(game_type, str) and game_type in game_type_set
        ]
        if not selected_game_types:
            selected_game_types = list(game_type_ids)

        team_set = set(allowed_teams)
        selected_teams = [
            team
            for team in defaults.get("teams", [])
            if isinstance(team, str) and team in team_set
        ]
        if not selected_teams:
            selected_teams = list(allowed_teams)

        min_year = int(options.get("min_year", fallback.start_year))
        max_year = int(options.get("max_year", fallback.end_year))
        if min_year > max_year:
            min_year, max_year = max_year, min_year

        return ResolvedConnectionSettings(
            game_types=selected_game_types,
            teams=selected_teams,
            start_year=min_year,
            end_year=max_year,
        )

    async def _pick_random_start_player(self, lobby: MultiplayerLobby) -> Dict[str, Any]:
        settings = lobby.connection_settings
        start_player_record = await getters.get_random_player_with_filters(
            teams=settings.teams,
            start_year=settings.start_year,
            end_year=settings.end_year,
            game_types=settings.game_types,
        )
        random_player = start_player_record.get("random_player") if start_player_record else None
        if random_player is None:
            raise InvalidActionError("No players are available for the selected settings.")

        return {
            "id": int(random_player["id"]),
            "full_name": str(random_player["fullName"]),
        }

    def _find_player_by_token(self, lobby: MultiplayerLobby, player_token: Optional[str]) -> Optional[MultiplayerSeat]:
        if not player_token:
            return None
        return next((seat for seat in lobby.players if seat.token == player_token), None)

    def _find_player_by_name(self, lobby: MultiplayerLobby, player_name: str) -> Optional[MultiplayerSeat]:
        normalized = player_name.strip().lower()
        return next((seat for seat in lobby.players if seat.name.strip().lower() == normalized), None)

    def _player_name_by_token(self, lobby: MultiplayerLobby, token: Optional[str]) -> Optional[str]:
        if not token:
            return None
        seat = self._find_player_by_token(lobby, token)
        return seat.name if seat else None

    def _other_player_token(self, lobby: MultiplayerLobby, token: str) -> Optional[str]:
        for seat in lobby.players:
            if seat.token != token:
                return seat.token
        return None

    def _apply_timeout_if_needed(self, lobby: MultiplayerLobby, now: float) -> None:
        current_round = lobby.round
        if not current_round or current_round.game_over:
            return
        if now < current_round.turn_deadline:
            return

        loser_token = current_round.active_player_token
        winner_token = self._other_player_token(lobby, loser_token)
        current_round.game_over = True
        current_round.winner_token = winner_token
        current_round.loser_token = loser_token
        current_round.end_reason = "timeout"

    async def _start_round(self, lobby: MultiplayerLobby) -> MultiplayerRound:
        if len(lobby.players) != MAX_PLAYERS:
            raise InvalidActionError("A game can only start when exactly two players are in the lobby.")

        now = time.time()
        start_player = await self._pick_random_start_player(lobby)
        active_player = random.choice(lobby.players)

        new_round = MultiplayerRound(
            current_path=[start_player],
            used_player_ids={int(start_player["id"])},
            step_teams=[],
            team_usage={},
            active_player_token=active_player.token,
            turn_started_at=now,
            turn_deadline=now + TURN_SECONDS,
        )
        lobby.round = new_round
        return new_round

    def _serialize_state(self, lobby: MultiplayerLobby, player_token: Optional[str]) -> Dict[str, Any]:
        now = time.time()
        self._apply_timeout_if_needed(lobby, now)
        current_round = lobby.round
        you = self._find_player_by_token(lobby, player_token)

        status = "waiting_for_player"
        if current_round and not current_round.game_over:
            status = "in_progress"
        elif current_round and current_round.game_over:
            status = "game_over"

        turn_deadline_epoch_ms: Optional[int] = None
        active_turn_remaining_ms = 0
        active_player_name: Optional[str] = None
        winner_name: Optional[str] = None
        loser_name: Optional[str] = None
        end_reason: Optional[str] = None

        if current_round:
            turn_deadline_epoch_ms = int(current_round.turn_deadline * 1000)
            active_turn_remaining_ms = max(int((current_round.turn_deadline - now) * 1000), 0)
            active_player_name = self._player_name_by_token(lobby, current_round.active_player_token)
            winner_name = self._player_name_by_token(lobby, current_round.winner_token)
            loser_name = self._player_name_by_token(lobby, current_round.loser_token)
            end_reason = current_round.end_reason

        return {
            "code": lobby.code,
            "status": status,
            "max_players": MAX_PLAYERS,
            "turn_seconds": TURN_SECONDS,
            "connection_cap": TEAM_SEASON_CONNECTION_CAP,
            "players": [
                {
                    "name": seat.name,
                    "is_you": you is not None and seat.token == you.token,
                }
                for seat in lobby.players
            ],
            "you_name": you.name if you else None,
            "is_joined": you is not None,
            "settings": serialize_resolved_connection_settings(lobby.connection_settings),
            "current_path": current_round.current_path if current_round else [],
            "step_teams": current_round.step_teams if current_round else [],
            "team_usage": current_round.team_usage if current_round else {},
            "active_player_name": active_player_name,
            "is_your_turn": bool(
                current_round and you and current_round.active_player_token == you.token and not current_round.game_over
            ),
            "turn_deadline_epoch_ms": turn_deadline_epoch_ms,
            "active_turn_remaining_ms": active_turn_remaining_ms,
            "game_over": bool(current_round and current_round.game_over),
            "winner_name": winner_name,
            "loser_name": loser_name,
            "end_reason": end_reason,
        }

    async def create_lobby(self) -> Dict[str, str]:
        async with self._lock:
            code = self._generate_lobby_code()
            while code in self._lobbies:
                code = self._generate_lobby_code()
            creator_token = secrets.token_urlsafe(24)
            default_settings = await self._get_lobby_default_settings()

            self._lobbies[code] = MultiplayerLobby(
                code=code,
                created_at=time.time(),
                creator_token=creator_token,
                connection_settings=default_settings,
            )
            return {"code": code, "join_path": f"/multiplayer/{code}", "creator_token": creator_token}

    def get_state(self, code: str, player_token: Optional[str]) -> Dict[str, Any]:
        lobby = self._lobbies.get(code.upper())
        if not lobby:
            raise LobbyNotFoundError("Lobby not found.")
        return self._serialize_state(lobby, player_token=player_token)

    async def join_lobby(self, code: str, player_name: str, player_token: Optional[str] = None) -> Dict[str, Any]:
        normalized_code = code.upper().strip()
        requested_name = (player_name or "").strip()
        if not requested_name:
            raise InvalidActionError("Player name is required.")

        async with self._lock:
            lobby = self._lobbies.get(normalized_code)
            if not lobby:
                raise LobbyNotFoundError("Lobby not found.")

            existing_by_token = self._find_player_by_token(lobby, player_token)
            if existing_by_token:
                return {
                    "player_token": existing_by_token.token,
                    "player_name": existing_by_token.name,
                    "state": self._serialize_state(lobby, player_token=existing_by_token.token),
                }

            if self._find_player_by_name(lobby, requested_name):
                raise DuplicateNameError("That player name is already taken in this lobby.")

            if len(lobby.players) >= MAX_PLAYERS:
                raise LobbyFullError("This lobby is already full.")

            new_token = secrets.token_urlsafe(24)
            lobby.players.append(
                MultiplayerSeat(
                    name=requested_name,
                    token=new_token,
                    joined_at=time.time(),
                )
            )

            if len(lobby.players) == MAX_PLAYERS and lobby.round is None:
                await self._start_round(lobby)

            return {
                "player_token": new_token,
                "player_name": requested_name,
                "state": self._serialize_state(lobby, player_token=new_token),
            }

    async def update_settings(
        self,
        code: str,
        player_token: str,
        creator_token: str,
        settings: Dict[str, Any],
    ) -> Dict[str, Any]:
        normalized_code = code.upper().strip()
        async with self._lock:
            lobby = self._lobbies.get(normalized_code)
            if not lobby:
                raise LobbyNotFoundError("Lobby not found.")

            seat = self._find_player_by_token(lobby, player_token)
            if not seat:
                raise InvalidTokenError("Player token is not valid for this lobby.")
            if creator_token != lobby.creator_token:
                raise InvalidActionError("Only the lobby creator can update settings.")

            lobby.connection_settings = await resolve_connection_settings(
                requested_settings=settings,
                default_relationship_types=DEFAULT_RELATIONSHIP_TYPES,
            )
            if len(lobby.players) == MAX_PLAYERS and lobby.round is None:
                await self._start_round(lobby)
            return self._serialize_state(lobby, player_token=player_token)

    async def make_guess(self, code: str, player_token: str, guessed_player_id: int) -> Dict[str, Any]:
        normalized_code = code.upper().strip()
        async with self._lock:
            lobby = self._lobbies.get(normalized_code)
            if not lobby:
                raise LobbyNotFoundError("Lobby not found.")

            seat = self._find_player_by_token(lobby, player_token)
            if not seat:
                raise InvalidTokenError("Player token is not valid for this lobby.")

            current_round = lobby.round
            if not current_round:
                raise InvalidActionError("Game has not started yet.")

            now = time.time()
            self._apply_timeout_if_needed(lobby, now)
            if current_round.game_over:
                return {
                    "valid": False,
                    "message": "Game is over.",
                    "invalid_player_name": None,
                    "invalid_reason": "Game is over.",
                    "overused_team_seasons": [],
                    "state": self._serialize_state(lobby, player_token=player_token),
                }

            if current_round.active_player_token != seat.token:
                return {
                    "valid": False,
                    "message": "It is not your turn.",
                    "invalid_player_name": None,
                    "invalid_reason": "It is not your turn.",
                    "overused_team_seasons": [],
                    "state": self._serialize_state(lobby, player_token=player_token),
                }

            guessed_name = await getters.get_name_from_playerid(int(guessed_player_id))
            if not guessed_name:
                return {
                    "valid": False,
                    "message": "Player not found.",
                    "invalid_player_name": None,
                    "invalid_reason": "Player not found.",
                    "overused_team_seasons": [],
                    "state": self._serialize_state(lobby, player_token=player_token),
                }

            if int(guessed_player_id) in current_round.used_player_ids:
                return {
                    "valid": False,
                    "message": "That player has already been used in this game.",
                    "invalid_player_name": guessed_name,
                    "invalid_reason": "That player has already been used in this game.",
                    "overused_team_seasons": [],
                    "state": self._serialize_state(lobby, player_token=player_token),
                }

            settings = lobby.connection_settings
            previous_player_id = int(current_round.current_path[-1]["id"])
            common_team_seasons = await getters.get_common_team_seasons(
                player1_id=previous_player_id,
                player2_id=int(guessed_player_id),
                teams=settings.teams,
                start_year=settings.start_year,
                end_year=settings.end_year,
                game_types=settings.game_types,
            )

            if not common_team_seasons:
                return {
                    "valid": False,
                    "message": "Not a valid teammate connection from the previous player.",
                    "invalid_player_name": guessed_name,
                    "invalid_reason": "Not a valid teammate connection from the previous player.",
                    "overused_team_seasons": [],
                    "state": self._serialize_state(lobby, player_token=player_token),
                }

            exhausted_links = [
                team_season
                for team_season in common_team_seasons
                if current_round.team_usage.get(team_season, 0) >= TEAM_SEASON_CONNECTION_CAP
            ]

            if exhausted_links:
                exhausted_links_text = ", ".join(exhausted_links)
                overuse_message = (
                    "That guess is blocked because these team-season links reached the usage cap: "
                    f"{exhausted_links_text}."
                )
                return {
                    "valid": False,
                    "message": overuse_message,
                    "invalid_player_name": guessed_name,
                    "invalid_reason": overuse_message,
                    "overused_team_seasons": exhausted_links,
                    "state": self._serialize_state(lobby, player_token=player_token),
                }

            guessed_player = {"id": int(guessed_player_id), "full_name": guessed_name}
            current_round.current_path.append(guessed_player)
            current_round.used_player_ids.add(int(guessed_player_id))
            current_round.step_teams.append(common_team_seasons)

            for team_season in common_team_seasons:
                current_round.team_usage[team_season] = current_round.team_usage.get(team_season, 0) + 1

            other_token = self._other_player_token(lobby, seat.token)
            if not other_token:
                raise InvalidActionError("Cannot switch turns with fewer than two players.")
            current_round.active_player_token = other_token
            current_round.turn_started_at = now
            current_round.turn_deadline = now + TURN_SECONDS

            return {
                "valid": True,
                "message": "Valid teammate. Turn switched.",
                "invalid_player_name": None,
                "invalid_reason": None,
                "overused_team_seasons": [],
                "state": self._serialize_state(lobby, player_token=player_token),
            }

    async def play_again(self, code: str, player_token: str) -> Dict[str, Any]:
        normalized_code = code.upper().strip()
        async with self._lock:
            lobby = self._lobbies.get(normalized_code)
            if not lobby:
                raise LobbyNotFoundError("Lobby not found.")

            seat = self._find_player_by_token(lobby, player_token)
            if not seat:
                raise InvalidTokenError("Player token is not valid for this lobby.")

            if len(lobby.players) != MAX_PLAYERS:
                raise InvalidActionError("Play again requires exactly two players.")

            await self._start_round(lobby)
            return self._serialize_state(lobby, player_token=player_token)


multiplayer_game_service = MultiplayerGameService()
