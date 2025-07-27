from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from backend.db import crud, models
from backend import schemas
from backend.api.main import get_db

router = APIRouter()

@router.get("/{player_id}", response_model=schemas.Player)
def get_player_by_id(player_id: int, db: Session = Depends(get_db)):
    player = crud.get_player(db, player_id=player_id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    return player

@router.get("/{player_id}/teammates", response_model=List[schemas.Player])
def get_player_teammates(player_id: int, db: Session = Depends(get_db)):
    teammates = crud.get_teammates_for_player(db, player_id=player_id)
    return teammates
