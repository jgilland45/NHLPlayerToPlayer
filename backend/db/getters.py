from typing import List, Dict, Any, Optional
from backend.db.session import get_graph_db

# NOTE: This adds a dependency on `thefuzz` library for fuzzy string matching.
# You may need to install it: pip install "thefuzz[speedup]"
from thefuzz import process
from collections import defaultdict

def _year_to_season(year: int) -> int:
    """Converts a 4-digit year (e.g., 2023) to an 8-digit NHL season format (e.g., 20232024)."""
    return year * 10000 + (year + 1)

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
    loweryear_season = _year_to_season(loweryear)
    upperyear_season = _year_to_season(upperyear)
    params = {"tricode": tricode.upper(), "loweryear": loweryear_season, "upperyear": upperyear_season}
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
    loweryear_season = _year_to_season(loweryear)
    upperyear_season = _year_to_season(upperyear)
    result = await db.run_query(query, {"loweryear": loweryear_season, "upperyear": upperyear_season})
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

async def get_teammates_of_player_with_options(
    playerid: int,
    teams: Optional[List[str]] = None,
    start_year: Optional[int] = None,
    end_year: Optional[int] = None,
    game_types: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """
    Finds all teammates of a player, with optional filters for teams, years, and game types.
    """
    db = get_graph_db()
    params = {"playerid": playerid}

    # Build the relationship type string for the query, e.g., ":TEAMMATE_IN_REGULAR_SEASON|TEAMMATE_IN_PLAYOFFS"
    rel_type_str = ""
    if game_types:
        rel_type_str = f":{'|'.join(game_types)}"

    # Build the WHERE clause dynamically
    where_clauses = ["p2.fullName IS NOT NULL"]
    if teams:
        where_clauses.append("r.team IN $teams")
        params["teams"] = [t.upper() for t in teams]
    if start_year is not None:
        where_clauses.append("r.season >= $start_year")
        params["start_year"] = _year_to_season(start_year)
    if end_year is not None:
        where_clauses.append("r.season <= $end_year")
        params["end_year"] = _year_to_season(end_year)

    where_str = "WHERE " + " AND ".join(where_clauses)

    query = f"""
        MATCH (p1:Player {{id: $playerid}})-[r{rel_type_str}]-(p2:Player)
        {where_str}
        RETURN DISTINCT p2.id AS id, p2.fullName AS full_name
    """
    result = await db.run_query(query, params)
    return [{"id": record["id"], "full_name": record["full_name"]} for record in result]

async def get_common_teams(
    player1_id: int,
    player2_id: int,
    start_year: Optional[int] = None,
    end_year: Optional[int] = None,
    game_types: Optional[List[str]] = None,
) -> List[str]:
    """Finds all teams where two players were teammates, with optional filters."""
    db = get_graph_db()
    params = {"p1_id": player1_id, "p2_id": player2_id}

    # Build the relationship type string for the query
    rel_type_str = ""
    if game_types:
        rel_type_str = f":{'|'.join(game_types)}"

    # Build the WHERE clause dynamically
    where_clauses = ["r.team IS NOT NULL"]
    if start_year is not None:
        where_clauses.append("r.season >= $start_year")
        params["start_year"] = _year_to_season(start_year)
    if end_year is not None:
        where_clauses.append("r.season <= $end_year")
        params["end_year"] = _year_to_season(end_year)

    where_str = "WHERE " + " AND ".join(where_clauses)

    query = f"""
        MATCH (p1:Player {{id: $p1_id}})-[r{rel_type_str}]-(p2:Player {{id: $p2_id}})
        {where_str}
        RETURN DISTINCT r.team AS teamid
        ORDER BY teamid
    """
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
    """
    Finds players matching a given name using fuzzy search.

    NOTE: This implementation fetches all players into memory to perform the
    fuzzy search. For a very large player database, this could be slow.
    An alternative would be to use a database extension like Neo4j's APOC
    for in-database fuzzy matching if available.
    """
    # 1. Get all players from the database. We can reuse the existing getter.
    all_players = await get_all_players()  # This returns [{"playerid": ..., "name": ...}]

    # 2. Create a mapping from a player name to a list of players with that name.
    # This handles cases where multiple players have the same name.
    player_map = defaultdict(list)
    for p in all_players:
        player_map[p["name"]].append(p)

    # 3. Use thefuzz to find the best matching names, limited to 25 results.
    best_matches = process.extract(name, player_map.keys(), limit=25)

    # 4. Filter matches by a score threshold and format the final result list.
    results = []
    for match_name, score in best_matches:
        # A score of 75 is a reasonable threshold to avoid very poor matches.
        if score >= 75:
            # Since multiple players can have the same name, extend the results list.
            players_with_match_name = player_map[match_name]
            for player_data in players_with_match_name:
                results.append({"id": player_data["playerid"], "full_name": player_data["name"]})
    return results

async def get_name_from_playerid(playerid: int) -> Optional[str]:
    """Gets a player's full name from their ID."""
    db = get_graph_db()
    query = "MATCH (p:Player {id: $playerid}) RETURN p.fullName AS name"
    result = await db.run_query(query, {"playerid": playerid})
    return result[0]["name"] if result else None

async def get_teams_from_playerid(
    playerid: int,
    start_year: Optional[int] = None,
    end_year: Optional[int] = None,
    game_types: Optional[List[str]] = None,
) -> List[str]:
    """Gets all unique team tricodes a player has played for, with optional filters."""
    db = get_graph_db()
    params = {"playerid": playerid}

    # Build the relationship type string for the query, e.g., ":TEAMMATE_IN_REGULAR_SEASON|TEAMMATE_IN_PLAYOFFS"
    rel_type_str = ""
    if game_types:
        rel_type_str = f":{'|'.join(game_types)}"

    # Build the WHERE clause dynamically
    where_clauses = ["r.team IS NOT NULL"]
    if start_year is not None:
        where_clauses.append("r.season >= $start_year")
        params["start_year"] = _year_to_season(start_year)
    if end_year is not None:
        where_clauses.append("r.season <= $end_year")
        params["end_year"] = _year_to_season(end_year)

    where_str = "WHERE " + " AND ".join(where_clauses)

    query = f"""
        MATCH (p:Player {{id: $playerid}})-[r{rel_type_str}]-()
        {where_str}
        RETURN DISTINCT r.team AS teamid
        ORDER BY teamid
    """
    result = await db.run_query(query, params)
    return [record["teamid"] for record in result]

async def find_shortest_path_between_players(
    player1_id: int,
    player2_id: int,
    start_year: Optional[int] = None,
    end_year: Optional[int] = None,
    game_types: Optional[List[str]] = None,
    include_players: Optional[List[int]] = None,
    exclude_players: Optional[List[int]] = None,
) -> List[Dict[str, Any]]:
    """
    Finds the shortest path between two players using APOC expandConfig,
    optimized by pushing year filters into relationshipFilter, reducing maxLevel,
    and minimizing post-filtering in Cypher for better performance.
    """
    db = get_graph_db()

    rel_types = game_types or ["TEAMMATE_IN_REGULAR_SEASON", "TEAMMATE_IN_PLAYOFFS"]

    # Start building relationshipFilter string with direction
    rel_filter = "|".join(rel_types) + ">"

    # Append year filters directly on relationship properties in the filter
    year_filters = []
    params = {
        "p1_id": player1_id,
        "p2_id": player2_id,
        "exclude_players": exclude_players or [],
        "include_players": include_players or [],
    }

    if start_year is not None:
        params["start_year"] = _year_to_season(start_year)
        year_filters.append(f"r.season >= $start_year")
    if end_year is not None:
        params["end_year"] = _year_to_season(end_year)
        year_filters.append(f"r.season <= $end_year")

    if year_filters:
        rel_filter += " AND " + " AND ".join(year_filters)

    query = f"""
    MATCH (start:Player {{id: $p1_id}}), (end:Player {{id: $p2_id}})
    CALL apoc.path.expandConfig(start, {{
      relationshipFilter: "{rel_filter}",
      minLevel: 1,
      terminatorNodes: [end],
      whitelistNodes: $include_players,
      blacklistNodes: $exclude_players,
      bfs: true,
      filterStartNode: true
    }})
    YIELD path
    RETURN [n IN nodes(path) | {{id: n.id, full_name: n.fullName}}] AS path_nodes
    ORDER BY length(path)
    LIMIT 1
    """
    print(query)
    print(params)

    result = await db.run_query(query, params)
    if not result:
        return []

    path_nodes = result[0]["path_nodes"]

    # Post-filter for include_players: ensure all included players appear on path
    if params["include_players"]:
        path_node_ids = {node["id"] for node in path_nodes}
        if not all(pid in path_node_ids for pid in params["include_players"]):
            return []  # No path includes all required players

    return path_nodes