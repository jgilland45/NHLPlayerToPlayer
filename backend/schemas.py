from pydantic import BaseModel
from typing import List

class PlayerBase(BaseModel):
    id: int
    full_name: str

class Player(PlayerBase):
    class Config:
        orm_mode = True # Allows Pydantic to read data from ORM models


class PathGameStartResponse(BaseModel):
    session_id: str
    start_player: Player
    end_player: Player
    current_path: List[Player]
    completed: bool


class PathGameGuessRequest(BaseModel):
    session_id: str
    player_id: int


class PathGameGuessResponse(BaseModel):
    valid: bool
    message: str
    current_path: List[Player]
    completed: bool
    last_step_teams: List[str] = []


class PathGameOptimalResponse(BaseModel):
    shortest_path: List[Player]
    shortest_path_length: int
    optimal_step_teams: List[List[str]] = []
