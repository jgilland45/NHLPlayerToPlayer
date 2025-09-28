import asyncio
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from backend.db import getters
from backend.db.session import get_graph_db, GraphDB
from backend import schemas

router = APIRouter()

# Mapping from user-friendly query params to Neo4j relationship types
GAME_TYPE_TO_REL_MAP = {
    "preseason": "TEAMMATE_IN_PRE_SEASON",
    "regular": "TEAMMATE_IN_REGULAR_SEASON",
    "playoffs": "TEAMMATE_IN_PLAYOFFS",
    "allstar": "TEAMMATE_IN_ALL_STAR",
    "worldcup_group": "TEAMMATE_IN_WORLD_CUP_GROUP",
    "worldcup_knockout": "TEAMMATE_IN_WORLD_CUP_KNOCKOUT",
    "worldcup_exhibition": "TEAMMATE_IN_WORLD_CUP_EXHIBITION",
    "olympics": "TEAMMATE_IN_OLYMPICS",
    "youngstars": "TEAMMATE_IN_YOUNG_STARS",
    "special": "TEAMMATE_IN_SPECIAL_EVENT",
    "canadacup": "TEAMMATE_IN_CANADA_CUP",
    "exhibition": "TEAMMATE_IN_EXHIBITION",
    "fournations": "TEAMMATE_IN_FOUR_NATIONS",
    "other": "TEAMMATE_IN_OTHER",
}

@router.get("/", response_model=List[schemas.Player])
async def get_all_players(db: GraphDB = Depends(get_graph_db)):
    """
    Returns a list of all players in the database.
    """
    players = await getters.get_all_players()
    # The getter returns keys 'playerid' and 'name', which we map to the schema's 'id' and 'full_name'.
    return [{"id": p["playerid"], "full_name": p["name"]} for p in players]

@router.get("/random", response_model=schemas.Player)
async def get_random_player(
        teams: Optional[List[str]] = Query(None, description="List of team tricodes to filter by (e.g., 'PIT', 'BOS')."),
        start_year: Optional[int] = Query(None, description="The starting season year for the teammate connection (e.g., 2016 for the 2016-17 season)."),
        end_year: Optional[int] = Query(None, description="The ending season year for the teammate connection (e.g., 2018 for the 2018-19 season)."),
        game_types: Optional[List[str]] = Query(None, description=f"List of game types to include. Valid options: {list(GAME_TYPE_TO_REL_MAP.keys())}"),
        db: GraphDB = Depends(get_graph_db)
    ):
    """
    Returns a single random player, with optional filters for teams, years, and game types.
    """
    db_game_types = None
    if game_types:
        db_game_types = []
        for gt in game_types:
            rel_type = GAME_TYPE_TO_REL_MAP.get(gt.lower())
            if not rel_type:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid game_type '{gt}'. Valid options are: {list(GAME_TYPE_TO_REL_MAP.keys())}"
                )
            db_game_types.append(rel_type)

    player_record = await getters.get_random_player_with_filters(
        teams=teams,
        start_year=start_year,
        end_year=end_year,
        game_types=db_game_types,
    )

    # The query returns a record with a 'random_player' field, which might be null.
    if not player_record or player_record["random_player"] is None:
        raise HTTPException(
            status_code=404,
            detail="No player found matching the specified criteria."
        )

    # Extract the Node object from the record.
    player_node = player_record["random_player"]

    return schemas.Player(id=player_node["id"], full_name=player_node["fullName"])

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
async def get_player_teammates(
    player_id: int,
    teams: Optional[List[str]] = Query(None, description="List of team tricodes to filter by (e.g., 'PIT', 'BOS')."),
    start_year: Optional[int] = Query(None, description="The starting season year for the teammate connection (e.g., 2016 for the 2016-17 season)."),
    end_year: Optional[int] = Query(None, description="The ending season year for the teammate connection (e.g., 2018 for the 2018-19 season)."),
    game_types: Optional[List[str]] = Query(None, description=f"List of game types to include. Valid options: {list(GAME_TYPE_TO_REL_MAP.keys())}"),
    db: GraphDB = Depends(get_graph_db),
):
    """
    Returns a list of players who have been a teammate of the given player,
    with optional filters for teams, years, and game types.
    """
    # Check if the base player exists
    player_name = await getters.get_name_from_playerid(player_id)
    if not player_name:
        raise HTTPException(status_code=404, detail="Player not found")

    db_game_types = None
    if game_types:
        db_game_types = []
        for gt in game_types:
            rel_type = GAME_TYPE_TO_REL_MAP.get(gt.lower())
            if not rel_type:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid game_type '{gt}'. Valid options are: {list(GAME_TYPE_TO_REL_MAP.keys())}"
                )
            db_game_types.append(rel_type)

    teammates = await getters.get_teammates_of_player_with_options(
        playerid=player_id,
        teams=teams,
        start_year=start_year,
        end_year=end_year,
        game_types=db_game_types,
    )
    return teammates

@router.get("/search/{player_name}", response_model=List[schemas.Player])
async def search_players_by_name(player_name: str, db: GraphDB = Depends(get_graph_db)):
    """
    Searches for players by name (case-insensitive, partial match).
    """
    players = await getters.get_players_by_name(player_name)
    return players

@router.get("/{player_id}/teams", response_model=List[str])
async def get_player_teams(
    player_id: int,
    start_year: Optional[int] = Query(None, description="The starting season year to filter teams by (e.g., 2016 for the 2016-17 season)."),
    end_year: Optional[int] = Query(None, description="The ending season year to filter teams by (e.g., 2018 for the 2018-19 season)."),
    game_types: Optional[List[str]] = Query(None, description=f"List of game types to include. Valid options: {list(GAME_TYPE_TO_REL_MAP.keys())}"),
    db: GraphDB = Depends(get_graph_db)
):
    """
    Returns a list of all team tricodes a player has played for, with optional filters.
    """
    # Check if player exists first to return a proper 404.
    player_name = await getters.get_name_from_playerid(player_id)
    if not player_name:
        raise HTTPException(status_code=404, detail="Player not found")

    db_game_types = None
    if game_types:
        db_game_types = []
        for gt in game_types:
            rel_type = GAME_TYPE_TO_REL_MAP.get(gt.lower())
            if not rel_type:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid game_type '{gt}'. Valid options are: {list(GAME_TYPE_TO_REL_MAP.keys())}"
                )
            db_game_types.append(rel_type)

    teams = await getters.get_teams_from_playerid(
        playerid=player_id,
        start_year=start_year,
        end_year=end_year,
        game_types=db_game_types,
    )
    return teams

@router.get("/common/teams/{player1_id}/{player2_id}", response_model=List[str])
async def get_common_teams_for_players(
    player1_id: int,
    player2_id: int,
    start_year: Optional[int] = Query(None, description="The starting season year to filter by (e.g., 2016 for the 2016-17 season)."),
    end_year: Optional[int] = Query(None, description="The ending season year to filter by (e.g., 2018 for the 2018-19 season)."),
    game_types: Optional[List[str]] = Query(None, description=f"List of game types to include. Valid options: {list(GAME_TYPE_TO_REL_MAP.keys())}"),
    db: GraphDB = Depends(get_graph_db)
):
    """
    Returns a list of team tricodes where two players were teammates, with optional filters.
    """
    # Check if both players exist first to provide a clearer error message.
    p1_name, p2_name = await asyncio.gather(
        getters.get_name_from_playerid(player1_id),
        getters.get_name_from_playerid(player2_id)
    )
    if not p1_name or not p2_name:
        raise HTTPException(status_code=404, detail="One or both players not found")

    db_game_types = None
    if game_types:
        db_game_types = []
        for gt in game_types:
            rel_type = GAME_TYPE_TO_REL_MAP.get(gt.lower())
            if not rel_type:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid game_type '{gt}'. Valid options are: {list(GAME_TYPE_TO_REL_MAP.keys())}"
                )
            db_game_types.append(rel_type)

    teams = await getters.get_common_teams(
        player1_id=player1_id,
        player2_id=player2_id,
        start_year=start_year,
        end_year=end_year,
        game_types=db_game_types,
    )
    return teams

@router.get("/path/{player1_id}/{player2_id}", response_model=List[schemas.Player])
async def get_shortest_path(
    player1_id: int,
    player2_id: int,
    start_year: Optional[int] = Query(None, description="The starting season year to filter by (e.g., 2016 for the 2016-17 season)."),
    end_year: Optional[int] = Query(None, description="The ending season year to filter by (e.g., 2018 for the 2018-19 season)."),
    game_types: Optional[List[str]] = Query(None, description=f"List of game types to include. Valid options: {list(GAME_TYPE_TO_REL_MAP.keys())}"),
    include_players: Optional[List[int]] = Query(None, description="List of player IDs that MUST be in the path."),
    exclude_players: Optional[List[int]] = Query(None, description="List of player IDs that MUST NOT be in the path."),
    db: GraphDB = Depends(get_graph_db)
):
    """
    Finds the shortest path of teammates connecting two players, with optional filters.
    """
    # Check if both players exist first to provide a clearer error message.
    p1_name, p2_name = await asyncio.gather(
        getters.get_name_from_playerid(player1_id),
        getters.get_name_from_playerid(player2_id)
    )
    if not p1_name or not p2_name:
        raise HTTPException(status_code=404, detail="One or both players not found")

    db_game_types = None
    if game_types:
        db_game_types = []
        for gt in game_types:
            rel_type = GAME_TYPE_TO_REL_MAP.get(gt.lower())
            if not rel_type:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid game_type '{gt}'. Valid options are: {list(GAME_TYPE_TO_REL_MAP.keys())}"
                )
            db_game_types.append(rel_type)

    path = await getters.find_shortest_path_between_players(
        player1_id=player1_id,
        player2_id=player2_id,
        start_year=start_year,
        end_year=end_year,
        game_types=db_game_types,
        include_players=include_players,
        exclude_players=exclude_players,
    )
    if not path:
        raise HTTPException(status_code=404, detail="No connection path found between the players with the given filters.")
    return path