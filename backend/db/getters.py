from typing import List, Dict, Any, Optional
from backend.db.session import get_graph_db

async def get_all_players() -> List[Dict[str, Any]]:
    db = get_graph_db()
    query = """
    MATCH (p:Player)
    WHERE p.fullName IS NOT NULL
    RETURN p.id AS playerid, p.fullName AS name
    ORDER BY p.fullName
    """
    result = await db.run_query(query)
    return [{"playerid": record["playerid"], "name": record["name"]} for record in result]

async def get_all_playerids() -> List[int]:
    db = get_graph_db()
    query = "MATCH (p:Player) RETURN p.id AS playerid"
    result = await db.run_query(query)
    return [record["playerid"] for record in result]

async def get_all_teams() -> List[str]:
    db = get_graph_db()
    query = "MATCH ()-[r]->() WHERE r.team IS NOT NULL RETURN DISTINCT r.team AS teamid ORDER BY teamid"
    result = await db.run_query(query)
    return [record["teamid"] for record in result]

async def get_all_games() -> List[int]:
    db = get_graph_db()
    query = "MATCH ()-[r]->() WHERE r.gameId IS NOT NULL RETURN DISTINCT r.gameId AS gameid"
    result = await db.run_query(query)
    return [record["gameid"] for record in result]

async def get_year_of_most_recent_game_played() -> Optional[str]:
    db = get_graph_db()
    query = "MATCH ()-[r]->() WHERE r.gameId IS NOT NULL RETURN r.gameId AS gameId ORDER BY gameId DESC LIMIT 1"
    result = await db.run_query(query)
    if not result:
        return None
    game_id = result[0]["gameId"]
    return str(game_id)[:4]

async def get_random_playerid() -> Optional[int]:
    db = get_graph_db()
    query = """
        MATCH (p:Player)
        WITH p, rand() AS r
        ORDER BY r
        LIMIT 1
        RETURN p.id AS playerid
    """
    result = await db.run_query(query)
    return result[0]["playerid"] if result else None

async def get_random_playerid_from_team_and_years(tricode: str, loweryear: int, upperyear: int) -> Optional[int]:
    db = get_graph_db()
    query = """
        MATCH (p:Player)-[r]-()
        WHERE r.team = $tricode
          AND r.season >= $loweryear
          AND r.season <= $upperyear
        WITH p, rand() AS random
        ORDER BY random
        LIMIT 1
        RETURN p.id AS playerid
    """
    params = {"tricode": tricode.upper(), "loweryear": loweryear, "upperyear": upperyear}
    result = await db.run_query(query, params)
    return result[0]["playerid"] if result else None

async def get_random_playerid_from_team(tricode: str) -> Optional[int]:
    db = get_graph_db()
    query = """
        MATCH (p:Player)-[r]-()
        WHERE r.team = $tricode
        WITH p, rand() AS random
        ORDER BY random
        LIMIT 1
        RETURN p.id AS playerid
    """
    result = await db.run_query(query, {"tricode": tricode.upper()})
    return result[0]["playerid"] if result else None

async def get_random_playerid_from_years(loweryear: int, upperyear: int) -> Optional[int]:
    db = get_graph_db()
    query = """
        MATCH (p:Player)-[r]-()
        WHERE r.season >= $loweryear
          AND r.season <= $upperyear
        WITH p, rand() AS random
        ORDER BY random
        LIMIT 1
        RETURN p.id AS playerid
    """
    result = await db.run_query(query, {"loweryear": loweryear, "upperyear": upperyear})
    return result[0]["playerid"] if result else None

async def get_all_teammates_of_player(playerid: int) -> List[Dict[str, Any]]:
    db = get_graph_db()
    query = """
        MATCH (p1:Player {id: $playerid})-[]-(p2:Player)
        WHERE p2.fullName IS NOT NULL
        RETURN DISTINCT p2.id AS id, p2.fullName AS full_name
    """
    result = await db.run_query(query, {"playerid": playerid})
    return [{"id": record["id"], "full_name": record["full_name"]} for record in result]

async def get_common_teams(player1_id: int, player2_id: int) -> List[str]:
    """Finds all teams where two players were teammates in the same game."""
    db = get_graph_db()
    query = """
        MATCH (p1:Player {id: $p1_id})-[r]-(p2:Player {id: $p2_id})
        RETURN DISTINCT r.team AS teamid
    """
    params = {"p1_id": player1_id, "p2_id": player2_id}
    result = await db.run_query(query, params)
    return [record["teamid"] for record in result]

async def get_reg_and_playoff_teammates_of_player(playerid: int) -> List[int]:
    """Finds all teammates of a player from regular season and playoff games only."""
    db = get_graph_db()
    query = """
        MATCH (p1:Player {id: $playerid})-[:TEAMMATE_IN_REGULAR_SEASON|:TEAMMATE_IN_PLAYOFFS]-(p2:Player)
        RETURN DISTINCT p2.id AS playerid
    """
    result = await db.run_query(query, {"playerid": playerid})
    return [record["playerid"] for record in result]

async def get_reg_and_playoff_common_teams(player1_id: int, player2_id: int) -> List[str]:
    """Finds common teams for two players, but only from regular season and playoff games."""
    db = get_graph_db()
    query = """
        MATCH (p1:Player {id: $p1_id})-[r:TEAMMATE_IN_REGULAR_SEASON|:TEAMMATE_IN_PLAYOFFS]-(p2:Player {id: $p2_id})
        RETURN DISTINCT r.team AS teamid
    """
    params = {"p1_id": player1_id, "p2_id": player2_id}
    result = await db.run_query(query, params)
    return [record["teamid"] for record in result]

async def get_players_by_name(name: str) -> List[Dict[str, Any]]:
    """Finds players matching a given full name (case-insensitive, partial match)."""
    db = get_graph_db()
    query = """
        MATCH (p:Player)
        WHERE toLower(p.fullName) CONTAINS toLower($name)
        RETURN p.id AS id, p.fullName AS full_name
        LIMIT 25
    """
    result = await db.run_query(query, {"name": name})
    return [{"id": record["id"], "full_name": record["full_name"]} for record in result]

async def get_name_from_playerid(playerid: int) -> Optional[str]:
    """Gets a player's full name from their ID."""
    db = get_graph_db()
    query = "MATCH (p:Player {id: $playerid}) RETURN p.fullName AS name"
    result = await db.run_query(query, {"playerid": playerid})
    return result[0]["name"] if result else None

async def get_teams_from_playerid(playerid: int) -> List[str]:
    """Gets all unique team tricodes a player has played for."""
    db = get_graph_db()
    query = """
        MATCH (p:Player {id: $playerid})-[r]-()
        RETURN DISTINCT r.team AS teamid
    """
    result = await db.run_query(query, {"playerid": playerid})
    return [record["teamid"] for record in result]

async def find_shortest_path_between_players(player1_id: int, player2_id: int) -> List[Dict[str, Any]]:
    """Finds the shortest path of teammates connecting two players."""
    db = get_graph_db()
    query = """
        MATCH path = shortestPath(
          (p1:Player {id: $p1_id})-[*]-(p2:Player {id: $p2_id})
        )
        // Return a list of player nodes in the path
        RETURN [node IN nodes(path) | {id: node.id, full_name: node.fullName}] AS path_nodes
    """
    params = {"p1_id": player1_id, "p2_id": player2_id}
    result = await db.run_query(query, params)
    # The query returns a list with a single record, which contains the list of nodes.
    return result[0]["path_nodes"] if result else []
