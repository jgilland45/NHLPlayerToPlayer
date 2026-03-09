import logging
import time
import random
import asyncio
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from uuid import uuid4

from backend.db import getters

_ALLOWED_GAME_TYPES = ["TEAMMATE_IN_REGULAR_SEASON", "TEAMMATE_IN_PLAYOFFS"]
logger = logging.getLogger("uvicorn.error")


@dataclass
class PathGameSession:
    session_id: str
    start_player: Dict[str, Any]
    end_player: Dict[str, Any]
    current_path: List[Dict[str, Any]]
    relationship_types: List[str]
    completed: bool = False


class PathGameService:
    """In-memory session service for the teammate path game."""

    def __init__(self):
        self._sessions: Dict[str, PathGameSession] = {}
        self._start_player_pool: List[int] = []

    async def _ensure_start_player_pool(self, min_size: int = 200) -> None:
        if len(self._start_player_pool) >= min_size:
            return

        logger.info("Loading start player pool for path game")
        try:
            sampled_ids = await asyncio.wait_for(getters.get_playerids_sample(limit=600), timeout=3.0)
        except Exception:
            logger.exception("Failed loading start player pool")
            raise ValueError("Database unavailable while loading player pool")

        self._start_player_pool = [int(player_id) for player_id in sampled_ids if player_id is not None]
        logger.info("Loaded start player pool size=%s", len(self._start_player_pool))

    async def _resolve_game_types(self) -> List[str]:
        # Game mode uses regular-season edges only for predictable performance.
        resolved_types = ["TEAMMATE_IN_REGULAR_SEASON"]
        logger.info("Resolved relationship types for game: %s", resolved_types)
        return resolved_types

    async def start_game(self, max_attempts: int = 25) -> PathGameSession:
        start_time = time.perf_counter()
        logger.info("Starting new path game generation (max_attempts=%s)", max_attempts)
        game_types = await self._resolve_game_types()
        await self._ensure_start_player_pool()

        if not self._start_player_pool:
            raise ValueError("No players available to start a game.")

        for attempt in range(1, max_attempts + 1):
            attempt_start = time.perf_counter()
            logger.info("Path game attempt %s/%s: selecting random start player", attempt, max_attempts)

            start_player_id = random.choice(self._start_player_pool)

            if start_player_id is None:
                logger.warning("Path game attempt %s: no random start player id found", attempt)
                logger.debug(
                    "Path game attempt %s finished in %.3fs",
                    attempt,
                    time.perf_counter() - attempt_start,
                )
                continue

            start_player_name = await getters.get_name_from_playerid(start_player_id)
            if not start_player_name:
                logger.warning("Path game attempt %s: random start player id=%s has no name", attempt, start_player_id)
                logger.debug(
                    "Path game attempt %s finished in %.3fs",
                    attempt,
                    time.perf_counter() - attempt_start,
                )
                continue

            start_player = {"id": start_player_id, "full_name": start_player_name}
            logger.info("Path game attempt %s: selected start player id=%s", attempt, start_player["id"])

            logger.info("Path game attempt %s: finding connected end player", attempt)
            end_lookup_started = time.perf_counter()
            end_player = await getters.get_random_connected_player_for_start(
                start_player_id=start_player["id"],
                game_types=game_types,
            )
            logger.info(
                "Path game attempt %s: end-player lookup elapsed=%.3fs",
                attempt,
                time.perf_counter() - end_lookup_started,
            )
            if not end_player:
                logger.warning(
                    "Path game attempt %s: no connected end player found for start id=%s",
                    attempt,
                    start_player["id"],
                )
                logger.debug(
                    "Path game attempt %s finished in %.3fs",
                    attempt,
                    time.perf_counter() - attempt_start,
                )
                continue
            logger.info("Path game attempt %s: selected end player id=%s", attempt, end_player["id"])

            session_id = str(uuid4())
            session = PathGameSession(
                session_id=session_id,
                start_player=start_player,
                end_player=end_player,
                current_path=[start_player],
                relationship_types=game_types,
            )
            self._sessions[session_id] = session
            logger.info(
                "Path game created successfully session_id=%s attempts=%s elapsed=%.3fs",
                session_id,
                attempt,
                time.perf_counter() - start_time,
            )
            return session

        logger.error("Unable to generate valid path game after %s attempts (elapsed=%.3fs)", max_attempts, time.perf_counter() - start_time)
        raise ValueError("Unable to generate a valid game session.")

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
            game_types=session.relationship_types,
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
            max_hops=6,
        )

        optimal_step_teams: List[List[str]] = []
        if len(shortest_path) >= 2:
            for idx in range(len(shortest_path) - 1):
                step_links = await getters.get_common_team_seasons(
                    player1_id=shortest_path[idx]["id"],
                    player2_id=shortest_path[idx + 1]["id"],
                    game_types=session.relationship_types,
                )
                optimal_step_teams.append(step_links)

        return {
            "shortest_path": shortest_path,
            "shortest_path_length": max(len(shortest_path) - 1, 0),
            "optimal_step_teams": optimal_step_teams,
        }


path_game_service = PathGameService()
