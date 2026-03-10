from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from backend import schemas
from backend.game.multiplayer_game import (
    DuplicateNameError,
    InvalidActionError,
    InvalidTokenError,
    LobbyFullError,
    LobbyNotFoundError,
    multiplayer_game_service,
)

router = APIRouter(prefix="/game/multiplayer", tags=["multiplayer-game"])


@router.post("/lobbies", response_model=schemas.MultiplayerCreateLobbyResponse)
async def create_multiplayer_lobby():
    return await multiplayer_game_service.create_lobby()


@router.get("/lobbies/{code}", response_model=schemas.MultiplayerStateResponse)
async def get_multiplayer_lobby_state(
    code: str,
    player_token: Optional[str] = Query(default=None),
):
    try:
        state = multiplayer_game_service.get_state(code=code, player_token=player_token)
        return {"state": state}
    except LobbyNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/lobbies/{code}/join", response_model=schemas.MultiplayerJoinResponse)
async def join_multiplayer_lobby(code: str, payload: schemas.MultiplayerJoinRequest):
    try:
        return await multiplayer_game_service.join_lobby(
            code=code,
            player_name=payload.name,
            player_token=payload.player_token,
        )
    except LobbyNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except LobbyFullError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except DuplicateNameError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except InvalidActionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/lobbies/{code}/guess", response_model=schemas.MultiplayerGuessResponse)
async def submit_multiplayer_guess(code: str, payload: schemas.MultiplayerGuessRequest):
    try:
        return await multiplayer_game_service.make_guess(
            code=code,
            player_token=payload.player_token,
            guessed_player_id=payload.player_id,
        )
    except LobbyNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except InvalidTokenError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    except InvalidActionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/lobbies/{code}/play-again", response_model=schemas.MultiplayerStateResponse)
async def multiplayer_play_again(code: str, payload: schemas.MultiplayerPlayAgainRequest):
    try:
        state = await multiplayer_game_service.play_again(
            code=code,
            player_token=payload.player_token,
        )
        return {"state": state}
    except LobbyNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except InvalidTokenError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    except InvalidActionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
