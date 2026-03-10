from __future__ import annotations

import asyncio
import copy
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Sequence

from backend.db import getters

_OPTIONS_CACHE_TTL_SECONDS = 60 * 10
_OPTIONS_CACHE: Dict[tuple[str, ...], tuple[float, Dict[str, Any]]] = {}
_OPTIONS_CACHE_LOCK = asyncio.Lock()

_RELATIONSHIP_TYPE_LABELS = {
    "TEAMMATE_IN_PRE_SEASON": "Preseason",
    "TEAMMATE_IN_REGULAR_SEASON": "Regular Season",
    "TEAMMATE_IN_PLAYOFFS": "Playoffs",
    "TEAMMATE_IN_ALL_STAR": "All-Star",
    "TEAMMATE_IN_WORLD_CUP_GROUP": "World Cup Group",
    "TEAMMATE_IN_WORLD_CUP_KNOCKOUT": "World Cup Knockout",
    "TEAMMATE_IN_WORLD_CUP_EXHIBITION": "World Cup Exhibition",
    "TEAMMATE_IN_OLYMPICS": "Olympics",
    "TEAMMATE_IN_YOUNG_STARS": "Young Stars",
    "TEAMMATE_IN_SPECIAL_EVENT": "Special Event",
    "TEAMMATE_IN_CANADA_CUP": "Canada Cup",
    "TEAMMATE_IN_EXHIBITION": "Exhibition",
    "TEAMMATE_IN_FOUR_NATIONS": "Four Nations",
    "TEAMMATE_IN_OTHER": "Other",
}
DEFAULT_RELATIONSHIP_TYPES = ["TEAMMATE_IN_REGULAR_SEASON"]


@dataclass
class ResolvedConnectionSettings:
    game_types: List[str]
    teams: List[str]
    start_year: int
    end_year: int


def _to_relationship_label(rel_type: str) -> str:
    if rel_type in _RELATIONSHIP_TYPE_LABELS:
        return _RELATIONSHIP_TYPE_LABELS[rel_type]

    normalized = rel_type.replace("TEAMMATE_IN_", "").replace("_", " ").strip().title()
    return normalized or rel_type


def _normalize_items(items: Optional[Sequence[str]], *, uppercase: bool = False) -> List[str]:
    if not items:
        return []
    normalized: List[str] = []
    seen = set()
    for raw in items:
        if not isinstance(raw, str):
            continue
        value = raw.strip()
        if uppercase:
            value = value.upper()
        if not value or value in seen:
            continue
        normalized.append(value)
        seen.add(value)
    return normalized


def _coerce_year(raw_year: Any, fallback: int) -> int:
    if raw_year is None:
        return int(fallback)
    try:
        return int(raw_year)
    except (TypeError, ValueError):
        return int(fallback)


async def get_connection_settings_options(
    default_relationship_types: Optional[Sequence[str]] = None,
) -> Dict[str, Any]:
    cache_key = tuple(_normalize_items(default_relationship_types or DEFAULT_RELATIONSHIP_TYPES))
    if not cache_key:
        cache_key = tuple(DEFAULT_RELATIONSHIP_TYPES)
    now = time.monotonic()
    cached = _OPTIONS_CACHE.get(cache_key)
    if cached and cached[0] > now:
        return copy.deepcopy(cached[1])

    async with _OPTIONS_CACHE_LOCK:
        refreshed_cached = _OPTIONS_CACHE.get(cache_key)
        if refreshed_cached and refreshed_cached[0] > time.monotonic():
            return copy.deepcopy(refreshed_cached[1])

        options = await _build_connection_settings_options(default_relationship_types=list(cache_key))
        _OPTIONS_CACHE[cache_key] = (time.monotonic() + _OPTIONS_CACHE_TTL_SECONDS, options)
        return copy.deepcopy(options)


async def _build_connection_settings_options(
    default_relationship_types: Optional[Sequence[str]] = None,
) -> Dict[str, Any]:
    relationship_types = await getters.get_existing_relationship_types()
    relationship_types = sorted(
        {
            rel_type
            for rel_type in relationship_types
            if isinstance(rel_type, str) and rel_type.startswith("TEAMMATE_IN_")
        },
        key=lambda rel_type: (_to_relationship_label(rel_type), rel_type),
    )

    if not relationship_types:
        relationship_types = list(DEFAULT_RELATIONSHIP_TYPES)

    teams = sorted(
        {
            team.strip().upper()
            for team in await getters.get_all_teams()
            if isinstance(team, str) and team.strip()
        }
    )

    season_bounds = await getters.get_season_year_bounds()
    current_year = datetime.utcnow().year
    min_year = int(season_bounds["min_year"]) if season_bounds else 1917
    max_year = int(season_bounds["max_year"]) if season_bounds else current_year
    if min_year > max_year:
        min_year, max_year = max_year, min_year

    preferred_defaults = _normalize_items(default_relationship_types or DEFAULT_RELATIONSHIP_TYPES)
    default_game_types = [rel_type for rel_type in preferred_defaults if rel_type in relationship_types]
    if not default_game_types:
        default_game_types = list(relationship_types)

    return {
        "game_types": [
            {
                "id": rel_type,
                "label": _to_relationship_label(rel_type),
            }
            for rel_type in relationship_types
        ],
        "teams": teams,
        "min_year": min_year,
        "max_year": max_year,
        "defaults": {
            "game_types": default_game_types,
            "teams": list(teams),
            "start_year": min_year,
            "end_year": max_year,
        },
    }


def serialize_resolved_connection_settings(settings: ResolvedConnectionSettings) -> Dict[str, Any]:
    return {
        "game_types": list(settings.game_types),
        "teams": list(settings.teams),
        "start_year": int(settings.start_year),
        "end_year": int(settings.end_year),
    }


async def resolve_connection_settings(
    requested_settings: Optional[Dict[str, Any]],
    default_relationship_types: Optional[Sequence[str]] = None,
) -> ResolvedConnectionSettings:
    options = await get_connection_settings_options(default_relationship_types=default_relationship_types)
    allowed_game_types = [entry["id"] for entry in options["game_types"]]
    allowed_game_type_set = set(allowed_game_types)
    allowed_teams = list(options["teams"])
    allowed_team_set = set(allowed_teams)
    defaults = options["defaults"]

    requested_game_types = _normalize_items(
        (requested_settings or {}).get("game_types"),
    )
    if not requested_game_types:
        requested_game_types = list(defaults["game_types"])
    if not requested_game_types:
        raise ValueError("At least one game type must be selected.")
    invalid_game_types = [rel_type for rel_type in requested_game_types if rel_type not in allowed_game_type_set]
    if invalid_game_types:
        raise ValueError(f"Unknown game type(s): {', '.join(invalid_game_types)}")

    ordered_game_types = [rel_type for rel_type in allowed_game_types if rel_type in set(requested_game_types)]

    requested_teams = _normalize_items(
        (requested_settings or {}).get("teams"),
        uppercase=True,
    )
    if not requested_teams:
        requested_teams = list(defaults["teams"])
    if not requested_teams:
        raise ValueError("At least one team must be selected.")
    invalid_teams = [team for team in requested_teams if team not in allowed_team_set]
    if invalid_teams:
        raise ValueError(f"Unknown team code(s): {', '.join(invalid_teams)}")

    ordered_teams = [team for team in allowed_teams if team in set(requested_teams)]

    min_year = int(options["min_year"])
    max_year = int(options["max_year"])
    requested_start_year = _coerce_year((requested_settings or {}).get("start_year"), int(defaults["start_year"]))
    requested_end_year = _coerce_year((requested_settings or {}).get("end_year"), int(defaults["end_year"]))

    start_year = max(min(requested_start_year, max_year), min_year)
    end_year = max(min(requested_end_year, max_year), min_year)
    if start_year > end_year:
        start_year, end_year = end_year, start_year

    return ResolvedConnectionSettings(
        game_types=ordered_game_types,
        teams=ordered_teams,
        start_year=start_year,
        end_year=end_year,
    )
