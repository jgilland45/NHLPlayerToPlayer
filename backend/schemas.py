from pydantic import BaseModel, Field
from typing import Dict, List, Literal, Optional

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


class MultiplayerCreateLobbyResponse(BaseModel):
    code: str
    join_path: str


class MultiplayerLobbyPlayer(BaseModel):
    name: str
    is_you: bool = False


class MultiplayerLobbyState(BaseModel):
    code: str
    status: Literal["waiting_for_player", "in_progress", "game_over"]
    max_players: int
    turn_seconds: int
    connection_cap: int
    players: List[MultiplayerLobbyPlayer]
    you_name: Optional[str] = None
    is_joined: bool = False
    current_path: List[Player] = Field(default_factory=list)
    step_teams: List[List[str]] = Field(default_factory=list)
    team_usage: Dict[str, int] = Field(default_factory=dict)
    active_player_name: Optional[str] = None
    is_your_turn: bool = False
    turn_deadline_epoch_ms: Optional[int] = None
    active_turn_remaining_ms: int = 0
    game_over: bool = False
    winner_name: Optional[str] = None
    loser_name: Optional[str] = None
    end_reason: Optional[str] = None


class MultiplayerJoinRequest(BaseModel):
    name: str = Field(min_length=1, max_length=24)
    player_token: Optional[str] = None


class MultiplayerJoinResponse(BaseModel):
    player_token: str
    player_name: str
    state: MultiplayerLobbyState


class MultiplayerGuessRequest(BaseModel):
    player_token: str = Field(min_length=1)
    player_id: int


class MultiplayerGuessResponse(BaseModel):
    valid: bool
    message: str
    invalid_player_name: Optional[str] = None
    invalid_reason: Optional[str] = None
    overused_team_seasons: List[str] = Field(default_factory=list)
    state: MultiplayerLobbyState


class MultiplayerPlayAgainRequest(BaseModel):
    player_token: str = Field(min_length=1)


class MultiplayerStateResponse(BaseModel):
    state: MultiplayerLobbyState
