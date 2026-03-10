from fastapi import APIRouter, HTTPException, Query
import httpx
import time
from typing import Any, Dict, Tuple

router = APIRouter()

_CACHE_TTL_SECONDS = 60 * 60 * 12
_standings_cache: Dict[str, Tuple[float, list[dict[str, Any]]]] = {}
_team_logo_cache: Dict[Tuple[str, str], Tuple[float, dict[str, str]]] = {}


def _get_cached_standings(standings_date: str) -> list[dict[str, Any]] | None:
    cached = _standings_cache.get(standings_date)
    if not cached:
        return None
    expires_at, standings = cached
    if time.time() > expires_at:
        _standings_cache.pop(standings_date, None)
        return None
    return standings


def _set_cached_standings(standings_date: str, standings: list[dict[str, Any]]) -> None:
    _standings_cache[standings_date] = (time.time() + _CACHE_TTL_SECONDS, standings)


def _get_cached_team_logo(cache_key: Tuple[str, str]) -> dict[str, str] | None:
    cached = _team_logo_cache.get(cache_key)
    if not cached:
        return None
    expires_at, payload = cached
    if time.time() > expires_at:
        _team_logo_cache.pop(cache_key, None)
        return None
    return payload


def _set_cached_team_logo(cache_key: Tuple[str, str], payload: dict[str, str]) -> None:
    _team_logo_cache[cache_key] = (time.time() + _CACHE_TTL_SECONDS, payload)


def _year_to_standings_date(year: str) -> str:
    normalized = (year or "").strip().replace("-", "")
    if len(normalized) != 8 or not normalized.isdigit():
        raise ValueError("year must be an 8-digit season like 20062007 or 20242025")

    # Use mid-season date so standings contain the right season branding.
    end_year = int(normalized[4:8])
    return f"{end_year}-01-15"


def _normalize_logo_url(logo_url: str, tricode: str) -> str:
    """Prefer primary logo variants and dark theme assets."""
    normalized = (logo_url or "").strip()
    if not normalized:
        return f"https://assets.nhle.com/logos/nhl/svg/{tricode}_dark.svg"

    # Keep dark variants for current UI styling.
    normalized = normalized.replace("_light.svg", "_dark.svg")

    # NHL standings can return secondary marks for some seasons (e.g., WSH).
    # Prefer the primary mark for consistency in gameplay UI.
    normalized = normalized.replace("_secondary_", "_")
    return normalized


@router.get("/team/logo")
async def get_team_logo(
    team_tricode: str = Query(..., min_length=3, max_length=3),
    year: str = Query(..., description="8-digit season like 20062007"),
):
    tricode = team_tricode.upper()
    normalized_year = (year or "").strip().replace("-", "")
    cache_key = (tricode, normalized_year)

    cached_payload = _get_cached_team_logo(cache_key)
    if cached_payload:
        return cached_payload

    try:
        standings_date = _year_to_standings_date(normalized_year)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    standings = _get_cached_standings(standings_date)
    if standings is None:
        url = f"https://api-web.nhle.com/v1/standings/{standings_date}"
        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                response = await client.get(url)
                response.raise_for_status()
        except httpx.HTTPError as exc:
            raise HTTPException(status_code=502, detail="Failed to fetch standings data") from exc
        standings = response.json().get("standings", [])
        _set_cached_standings(standings_date, standings)

    team_row = next((row for row in standings if row.get("teamAbbrev", {}).get("default") == tricode), None)

    if not team_row:
        raise HTTPException(status_code=404, detail=f"Team {tricode} not found for season {year}")

    raw_logo = team_row.get("teamLogo") or f"https://assets.nhle.com/logos/nhl/svg/{tricode}_dark.svg"
    logo = _normalize_logo_url(str(raw_logo), tricode)

    team_name = team_row.get("teamName", {}).get("default") or tricode
    payload = {"logo": logo, "name": team_name}
    _set_cached_team_logo(cache_key, payload)
    return payload
