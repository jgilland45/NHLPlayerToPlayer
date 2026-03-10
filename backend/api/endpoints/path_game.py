import logging
import time
from typing import Optional

from fastapi import APIRouter, HTTPException

from backend import schemas
from backend.game.connection_settings import serialize_resolved_connection_settings
from backend.game.path_game import path_game_service

router = APIRouter(prefix="/game/path", tags=["path-game"])
logger = logging.getLogger("uvicorn.error")


@router.get("/settings", response_model=schemas.ConnectionSettingsOptionsResponse)
async def get_path_game_settings():
    options = await path_game_service.get_settings_options()
    return {"options": options}


@router.post("/start", response_model=schemas.PathGameStartResponse)
async def start_path_game(payload: Optional[schemas.PathGameStartRequest] = None):
    request_start = time.perf_counter()
    logger.info("POST /game/path/start received")
    try:
        requested_settings = payload.settings.model_dump() if payload and payload.settings else None
        session = await path_game_service.start_game(requested_settings=requested_settings)
    except ValueError as exc:
        logger.exception("POST /game/path/start failed: %s", str(exc))
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    logger.info(
        "POST /game/path/start completed session_id=%s elapsed=%.3fs",
        session.session_id,
        time.perf_counter() - request_start,
    )

    return {
        "session_id": session.session_id,
        "start_player": session.start_player,
        "end_player": session.end_player,
        "current_path": session.current_path,
        "completed": session.completed,
        "settings": serialize_resolved_connection_settings(session.connection_settings),
    }


@router.post("/guess", response_model=schemas.PathGameGuessResponse)
async def make_path_game_guess(payload: schemas.PathGameGuessRequest):
    logger.info("POST /game/path/guess session_id=%s guessed_player_id=%s", payload.session_id, payload.player_id)
    session = path_game_service.get_session(payload.session_id)
    if not session:
        logger.warning("POST /game/path/guess session not found session_id=%s", payload.session_id)
        raise HTTPException(status_code=404, detail="Session not found")

    result = await path_game_service.make_guess(
        session_id=payload.session_id,
        guessed_player_id=payload.player_id,
    )
    return result


@router.get("/{session_id}/optimal", response_model=schemas.PathGameOptimalResponse)
async def get_optimal_path_solution(session_id: str):
    logger.info("GET /game/path/%s/optimal", session_id)
    try:
        result = await path_game_service.get_optimal_solution(session_id)
        if not result:
            logger.warning("GET /game/path/%s/optimal session not found", session_id)
            raise HTTPException(status_code=404, detail="Session not found")
        return result
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("GET /game/path/%s/optimal failed: %s", session_id, str(exc))
        raise HTTPException(status_code=500, detail="Failed to compute optimal solution.") from exc
