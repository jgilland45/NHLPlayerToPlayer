import asyncio
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from backend.db import getters
from backend.db.session import get_graph_db, GraphDB
from backend import schemas

router = APIRouter()

@router.get("/", response_model=List[schemas.Player])
async def get_all_players(db: GraphDB = Depends(get_graph_db)):
    """
    Returns a list of all players in the database.
    """
    players = await getters.get_all_players()
    # The getter returns keys 'playerid' and 'name', which we map to the schema's 'id' and 'full_name'.
    return [{"id": p["playerid"], "full_name": p["name"]} for p in players]

@router.get("/{player_id}", response_model=schemas.Player)
async def get_player_by_id(player_id: int, db: GraphDB = Depends(get_graph_db)):
    """
    Returns a single player's details by their ID.
    """
    name = await getters.get_name_from_playerid(player_id)
    if not name:
        raise HTTPException(status_code=404, detail="Player not found")
    return schemas.Player(id=player_id, full_name=name)

@router.get("/{player_id}/teammates", response_model=List[schemas.Player])
async def get_player_teammates(player_id: int, db: GraphDB = Depends(get_graph_db)):
    """
    Returns a list of all players who have been a teammate of the given player.
    """
    # The getter now returns a list of dicts that match the schemas.Player model.
    teammates = await getters.get_all_teammates_of_player(player_id)
    return teammates

@router.get("/search/{player_name}", response_model=List[schemas.Player])
async def search_players_by_name(player_name: str, db: GraphDB = Depends(get_graph_db)):
    """
    Searches for players by name (case-insensitive, partial match).
    """
    players = await getters.get_players_by_name(player_name)
    return players

@router.get("/{player_id}/teams", response_model=List[str])
async def get_player_teams(player_id: int, db: GraphDB = Depends(get_graph_db)):
    """
    Returns a list of all team tricodes a player has played for.
    """
    teams = await getters.get_teams_from_playerid(player_id)
    if not teams:
        # Check if player exists at all to return a proper 404 if they have no teams.
        player_name = await getters.get_name_from_playerid(player_id)
        if not player_name:
            raise HTTPException(status_code=404, detail="Player not found")
    return teams

@router.get("/common/teams/{player1_id}/{player2_id}", response_model=List[str])
async def get_common_teams_for_players(player1_id: int, player2_id: int, db: GraphDB = Depends(get_graph_db)):
    """
    Returns a list of team tricodes where two players were teammates.
    """
    # Check if both players exist first to provide a clearer error message.
    p1_name, p2_name = await asyncio.gather(
        getters.get_name_from_playerid(player1_id),
        getters.get_name_from_playerid(player2_id)
    )
    if not p1_name or not p2_name:
        raise HTTPException(status_code=404, detail="One or both players not found")

    teams = await getters.get_common_teams(player1_id, player2_id)
    return teams

@router.get("/path/{player1_id}/{player2_id}", response_model=List[schemas.Player])
async def get_shortest_path(player1_id: int, player2_id: int, db: GraphDB = Depends(get_graph_db)):
    """
    Finds the shortest path of teammates connecting two players.
    """
    # Check if both players exist first to provide a clearer error message.
    p1_name, p2_name = await asyncio.gather(
        getters.get_name_from_playerid(player1_id),
        getters.get_name_from_playerid(player2_id)
    )
    if not p1_name or not p2_name:
        raise HTTPException(status_code=404, detail="One or both players not found")

    path = await getters.find_shortest_path_between_players(player1_id, player2_id)
    if not path:
        raise HTTPException(status_code=404, detail="No connection path found between the players.")
    return path
