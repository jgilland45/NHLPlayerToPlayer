import logging
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from uuid import uuid4

from backend.db import getters
from backend.game.connection_settings import (
    DEFAULT_RELATIONSHIP_TYPES,
    ResolvedConnectionSettings,
    get_connection_settings_options,
    resolve_connection_settings,
    serialize_resolved_connection_settings,
)

logger = logging.getLogger("uvicorn.error")


@dataclass
class PathGameSession:
    session_id: str
    start_player: Dict[str, Any]
    end_player: Dict[str, Any]
    current_path: List[Dict[str, Any]]
    connection_settings: ResolvedConnectionSettings
    completed: bool = False


class PathGameService:
    """In-memory session service for the teammate path game."""

    def __init__(self):
        self._sessions: Dict[str, PathGameSession] = {}

    async def get_settings_options(self) -> Dict[str, Any]:
        return await get_connection_settings_options(default_relationship_types=DEFAULT_RELATIONSHIP_TYPES)

    async def start_game(
        self,
        requested_settings: Optional[Dict[str, Any]] = None,
        max_attempts: int = 25,
    ) -> PathGameSession:
        start_time = time.perf_counter()
        logger.info("Starting new path game generation (max_attempts=%s)", max_attempts)

        connection_settings = await resolve_connection_settings(
            requested_settings=requested_settings,
            default_relationship_types=DEFAULT_RELATIONSHIP_TYPES,
        )

        for attempt in range(1, max_attempts + 1):
            attempt_start = time.perf_counter()
            logger.info("Path game attempt %s/%s: selecting filtered start player", attempt, max_attempts)

            start_player_record = await getters.get_random_player_with_filters(
                teams=connection_settings.teams,
                start_year=connection_settings.start_year,
                end_year=connection_settings.end_year,
                game_types=connection_settings.game_types,
            )

            random_player = start_player_record.get("random_player") if start_player_record else None
            if random_player is None:
                logger.warning("Path game attempt %s: no start player found for selected filters", attempt)
                continue

            start_player = {
                "id": int(random_player["id"]),
                "full_name": str(random_player["fullName"]),
            }
            logger.info("Path game attempt %s: selected start player id=%s", attempt, start_player["id"])

            logger.info("Path game attempt %s: finding connected end player", attempt)
            end_lookup_started = time.perf_counter()
            end_player = await getters.get_random_connected_player_for_start(
                start_player_id=start_player["id"],
                teams=connection_settings.teams,
                start_year=connection_settings.start_year,
                end_year=connection_settings.end_year,
                game_types=connection_settings.game_types,
            )
            logger.info(
                "Path game attempt %s: end-player lookup elapsed=%.3fs",
                attempt,
                time.perf_counter() - end_lookup_started,
            )

            if not end_player or int(end_player["id"]) == start_player["id"]:
                logger.warning(
                    "Path game attempt %s: no connected end player for start id=%s",
                    attempt,
                    start_player["id"],
                )
                logger.debug(
                    "Path game attempt %s finished in %.3fs",
                    attempt,
                    time.perf_counter() - attempt_start,
                )
                continue

            session_id = str(uuid4())
            session = PathGameSession(
                session_id=session_id,
                start_player=start_player,
                end_player=end_player,
                current_path=[start_player],
                connection_settings=connection_settings,
            )
            self._sessions[session_id] = session
            logger.info(
                "Path game created successfully session_id=%s attempts=%s elapsed=%.3fs settings=%s",
                session_id,
                attempt,
                time.perf_counter() - start_time,
                serialize_resolved_connection_settings(connection_settings),
            )
            return session

        logger.error(
            "Unable to generate valid path game after %s attempts (elapsed=%.3fs)",
            max_attempts,
            time.perf_counter() - start_time,
        )
        raise ValueError("Unable to generate a valid game session with the selected settings.")

    def get_session(self, session_id: str) -> Optional[PathGameSession]:
        return self._sessions.get(session_id)

    async def make_guess(self, session_id: str, guessed_player_id: int) -> dict:
        session = self.get_session(session_id)
        if not session:
            return {
                "valid": False,
                "message": "Session not found.",
                "current_path": [],
                "completed": False,
                "last_step_teams": [],
            }

        if session.completed:
            return {
                "valid": False,
                "message": "Game already completed.",
                "current_path": session.current_path,
                "completed": True,
                "last_step_teams": [],
            }

        guessed_name = await getters.get_name_from_playerid(guessed_player_id)
        if not guessed_name:
            return {
                "valid": False,
                "message": "Player not found.",
                "current_path": session.current_path,
                "completed": False,
                "last_step_teams": [],
            }

        existing_ids = {player["id"] for player in session.current_path}
        if guessed_player_id in existing_ids:
            return {
                "valid": False,
                "message": "That player is already in your path.",
                "current_path": session.current_path,
                "completed": False,
                "last_step_teams": [],
            }

        previous_player_id = session.current_path[-1]["id"]
        common_team_seasons = await getters.get_common_team_seasons(
            player1_id=previous_player_id,
            player2_id=guessed_player_id,
            teams=session.connection_settings.teams,
            start_year=session.connection_settings.start_year,
            end_year=session.connection_settings.end_year,
            game_types=session.connection_settings.game_types,
        )

        if not common_team_seasons:
            return {
                "valid": False,
                "message": "Not a valid teammate connection from your current player.",
                "current_path": session.current_path,
                "completed": False,
                "last_step_teams": [],
            }

        guessed_player = {"id": guessed_player_id, "full_name": guessed_name}
        session.current_path.append(guessed_player)

        if guessed_player_id == session.end_player["id"]:
            session.completed = True
            return {
                "valid": True,
                "message": "Path complete! You reached the final player.",
                "current_path": session.current_path,
                "completed": True,
                "last_step_teams": common_team_seasons,
            }

        return {
            "valid": True,
            "message": "Valid teammate. Keep going.",
            "current_path": session.current_path,
            "completed": False,
            "last_step_teams": common_team_seasons,
        }

    async def get_optimal_solution(self, session_id: str) -> Optional[dict]:
        session = self.get_session(session_id)
        if not session:
            return None

        shortest_path = await getters.find_shortest_path_for_game(
            player1_id=session.start_player["id"],
            player2_id=session.end_player["id"],
            teams=session.connection_settings.teams,
            start_year=session.connection_settings.start_year,
            end_year=session.connection_settings.end_year,
            game_types=session.connection_settings.game_types,
            max_hops=6,
        )

        optimal_step_teams: List[List[str]] = []
        if len(shortest_path) >= 2:
            for idx in range(len(shortest_path) - 1):
                step_links = await getters.get_common_team_seasons(
                    player1_id=shortest_path[idx]["id"],
                    player2_id=shortest_path[idx + 1]["id"],
                    teams=session.connection_settings.teams,
                    start_year=session.connection_settings.start_year,
                    end_year=session.connection_settings.end_year,
                    game_types=session.connection_settings.game_types,
                )
                optimal_step_teams.append(step_links)

        return {
            "shortest_path": shortest_path,
            "shortest_path_length": max(len(shortest_path) - 1, 0),
            "optimal_step_teams": optimal_step_teams,
        }


path_game_service = PathGameService()
