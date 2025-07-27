from pydantic import BaseModel
from typing import List

class PlayerBase(BaseModel):
    id: int
    full_name: str

class Player(PlayerBase):
    class Config:
        orm_mode = True # Allows Pydantic to read data from ORM models
