import logging
import time
import asyncio
import random
from typing import List, Dict, Any, Optional
from backend.db.session import get_graph_db

# NOTE: This adds a dependency on `thefuzz` library for fuzzy string matching.
# You may need to install it: pip install "thefuzz[speedup]"
from thefuzz import process
from collections import defaultdict, deque

_DEFAULT_PATH_REL_TYPES = ["TEAMMATE_IN_REGULAR_SEASON", "TEAMMATE_IN_PLAYOFFS"]
logger = logging.getLogger("uvicorn.error")

def _year_to_season(year: int) -> int:
    """Converts a 4-digit year (e.g., 2023) to an 8-digit NHL season format (e.g., 20232024)."""
    return year * 10000 + (year + 1)


def _season_to_label(season: int) -> str:
    """Converts 8-digit season format (e.g., 20252026) to display label (2025-26)."""
    start_year = season // 10000
    end_year = season % 10000
    return f"{start_year}-{str(end_year)[-2:]}"

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


async def get_playerids_sample(limit: int = 2000) -> List[int]:
    """Returns a bounded sample of player IDs for fast in-memory random selection."""
    db = get_graph_db()
    query = """
        MATCH (p:Player)
        WHERE p.id IS NOT NULL
        RETURN p.id AS playerid
        LIMIT $limit
    """
    result = await db.run_query(query, {"limit": int(limit)})
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


async def get_season_year_bounds() -> Optional[Dict[str, int]]:
    """
    Returns the min/max available season start years from relationship data.
    Example: season 20232024 returns year 2023.
    """
    db = get_graph_db()
    query = """
        MATCH ()-[r]-()
        WHERE r.season IS NOT NULL
        RETURN min(r.season) AS min_season, max(r.season) AS max_season
    """
    result = await db.run_query(query)
    if not result:
        return None

    min_season = result[0].get("min_season")
    max_season = result[0].get("max_season")
    if min_season is None or max_season is None:
        return None

    return {
        "min_year": int(min_season) // 10000,
        "max_year": int(max_season) // 10000,
    }


async def get_existing_relationship_types(candidate_types: Optional[List[str]] = None) -> List[str]:
    """
    Returns relationship types currently present in the database.
    If candidate_types is provided, only matching types are returned.
    """
    db = get_graph_db()
    query = "CALL db.relationshipTypes() YIELD relationshipType RETURN relationshipType"
    try:
        # Schema introspection can occasionally stall; fail fast and fall back.
        result = await asyncio.wait_for(db.run_query(query), timeout=2.0)
    except asyncio.TimeoutError:
        logger.error("Timed out fetching relationship types from Neo4j schema")
        return candidate_types or []
    except Exception:
        logger.exception("Failed fetching relationship types from Neo4j schema")
        return candidate_types or []

    existing = [record["relationshipType"] for record in result]

    if candidate_types is None:
        return existing

    candidate_set = set(candidate_types)
    return [rel_type for rel_type in existing if rel_type in candidate_set]

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
    bounds_query = """
        MATCH (p:Player)
        WHERE p.id IS NOT NULL
        RETURN min(p.id) AS min_id, max(p.id) AS max_id
    """
    bounds = await db.run_query(bounds_query)
    if not bounds or bounds[0]["min_id"] is None or bounds[0]["max_id"] is None:
        return None

    min_id = int(bounds[0]["min_id"])
    max_id = int(bounds[0]["max_id"])
    if max_id < min_id:
        return None

    random_target = min_id + int((max_id - min_id + 1) * random.random())

    forward_query = """
        MATCH (p:Player)
        WHERE p.id >= $target_id
        RETURN p.id AS playerid
        ORDER BY p.id
        LIMIT 1
    """
    result = await db.run_query(forward_query, {"target_id": random_target})
    if result:
        return result[0]["playerid"]

    wrap_query = """
        MATCH (p:Player)
        WHERE p.id IS NOT NULL
        RETURN p.id AS playerid
        ORDER BY p.id
        LIMIT 1
    """
    wrap_result = await db.run_query(wrap_query)
    return wrap_result[0]["playerid"] if wrap_result else None

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

async def get_random_player_with_filters(
    teams: Optional[List[str]] = None,
    start_year: Optional[int] = None,
    end_year: Optional[int] = None,
    game_types: Optional[List[str]] = None,
) -> Optional[Dict[str, Any]]:
    """
    Gets a random player (ID and name) based on a combination of optional filters.
    """
    db = get_graph_db()
    params: Dict[str, Any] = {}

    rel_type_str = ""
    if game_types:
        rel_type_str = f":{'|'.join(game_types)}"

    where_clauses = []
    if teams:
        where_clauses.append("r.team IN $teams")
        params["teams"] = [t.upper() for t in teams]
    if start_year is not None:
        where_clauses.append("r.season >= $start_year")
        params["start_year"] = _year_to_season(start_year)
    if end_year is not None:
        where_clauses.append("r.season <= $end_year")
        params["end_year"] = _year_to_season(end_year)

    where_str = ""
    if where_clauses:
        where_str = "WHERE " + " AND ".join(where_clauses)

    # Select a random distinct player directly, without collecting all matches
    # into memory. This keeps memory usage bounded for broad filter sets.
    query = f"""
        MATCH (p:Player)-[r{rel_type_str}]-()
        {where_str}
        WITH DISTINCT p, rand() AS random_value
        ORDER BY random_value
        LIMIT 1
        RETURN p AS random_player
    """
    result = await db.run_query(query, params)
    if not result:
        return {"random_player": None}
    return {"random_player": result[0]["random_player"]}

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
    params: Dict[str, Any] = {"playerid": playerid}

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
    params: Dict[str, Any] = {"p1_id": player1_id, "p2_id": player2_id}

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


async def get_common_team_seasons(
    player1_id: int,
    player2_id: int,
    teams: Optional[List[str]] = None,
    start_year: Optional[int] = None,
    end_year: Optional[int] = None,
    game_types: Optional[List[str]] = None,
) -> List[str]:
    """Returns distinct common teammate links as 'TEAM YYYY-YY' labels."""
    db = get_graph_db()
    params: Dict[str, Any] = {"p1_id": player1_id, "p2_id": player2_id}

    rel_type_str = ""
    if game_types:
        rel_type_str = f":{'|'.join(game_types)}"

    where_clauses = ["r.team IS NOT NULL", "r.season IS NOT NULL"]
    if teams:
        where_clauses.append("r.team IN $teams")
        params["teams"] = [team.upper() for team in teams]
    if start_year is not None:
        where_clauses.append("r.season >= $start_year")
        params["start_year"] = _year_to_season(start_year)
    if end_year is not None:
        where_clauses.append("r.season <= $end_year")
        params["end_year"] = _year_to_season(end_year)

    query = f"""
        MATCH (p1:Player {{id: $p1_id}})-[r{rel_type_str}]-(p2:Player {{id: $p2_id}})
        WHERE {" AND ".join(where_clauses)}
        RETURN DISTINCT r.team AS teamid, r.season AS season
        ORDER BY season DESC, teamid ASC
    """
    result = await db.run_query(query, params)
    return [f"{record['teamid']} {_season_to_label(int(record['season']))}" for record in result]

async def get_reg_and_playoff_teammates_of_player(playerid: int) -> List[int]:
    """Finds all teammates of a player from regular season and playoff games only."""
    db = get_graph_db()
    rel_types = await get_existing_relationship_types(_DEFAULT_PATH_REL_TYPES)
    if not rel_types:
        return []

    rel_pattern = "|".join(rel_types)
    query = """
        MATCH (p1:Player {id: $playerid})-[:%s]-(p2:Player)
        RETURN DISTINCT p2.id AS playerid
    """ % rel_pattern
    result = await db.run_query(query, {"playerid": playerid})
    return [record["playerid"] for record in result]

async def get_reg_and_playoff_common_teams(player1_id: int, player2_id: int) -> List[str]:
    """Finds common teams for two players, but only from regular season and playoff games."""
    db = get_graph_db()
    rel_types = await get_existing_relationship_types(_DEFAULT_PATH_REL_TYPES)
    if not rel_types:
        return []

    rel_pattern = "|".join(rel_types)
    query = """
        MATCH (p1:Player {id: $p1_id})-[r:%s]-(p2:Player {id: $p2_id})
        RETURN DISTINCT r.team AS teamid
    """ % rel_pattern
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
    params: Dict[str, Any] = {"playerid": playerid}

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
    max_hops: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """
    Finds the shortest path between two players using APOC expandConfig,
    optimized by pushing year filters into relationshipFilter, reducing maxLevel,
    and minimizing post-filtering in Cypher for better performance.
    """
    db = get_graph_db()

    if game_types:
        rel_types = await get_existing_relationship_types(game_types)
    else:
        rel_types = await get_existing_relationship_types(_DEFAULT_PATH_REL_TYPES)

    if not rel_types:
        return []

    rel_filter = "|".join(rel_types) + ">"

    year_filters = []
    params: Dict[str, Any] = {
        "p1_id": player1_id,
        "p2_id": player2_id,
        "exclude_players": exclude_players or [],
        "include_players": include_players or [],
    }

    if start_year is not None:
        params["start_year"] = _year_to_season(start_year)
        year_filters.append("r.season >= $start_year")
    if end_year is not None:
        params["end_year"] = _year_to_season(end_year)
        year_filters.append("r.season <= $end_year")

    if year_filters:
        rel_filter += " AND " + " AND ".join(year_filters)

    max_level_line = f"maxLevel: {int(max_hops)}," if max_hops is not None else ""
    query = f"""
    MATCH (start:Player {{id: $p1_id}}), (end:Player {{id: $p2_id}})
    CALL apoc.path.expandConfig(start, {{
      relationshipFilter: "{rel_filter}",
      minLevel: 1,
      {max_level_line}
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

    logger.debug("Running shortest-path query p1=%s p2=%s rel_types=%s max_hops=%s", player1_id, player2_id, rel_types, max_hops)

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


async def get_random_connected_player_for_start(
    start_player_id: int,
    teams: Optional[List[str]] = None,
    start_year: Optional[int] = None,
    end_year: Optional[int] = None,
    game_types: Optional[List[str]] = None,
    min_hops: int = 2,
    max_hops: int = 6,
    sample_limit: int = 300,
) -> Optional[Dict[str, Any]]:
    """
    Returns a random player connected to the given start player within bounded
    hop distance. Uses APOC path expansion with a hard sample limit to avoid
    explosive variable-length traversals.
    """
    started = time.perf_counter()
    db = get_graph_db()
    if game_types:
        rel_types = await get_existing_relationship_types(game_types)
    else:
        rel_types = await get_existing_relationship_types(_DEFAULT_PATH_REL_TYPES)

    if not rel_types:
        logger.warning("No relationship types available for connected-player lookup")
        return None

    rel_filter = "|".join(rel_types)
    relationship_predicates = ["rel.team IS NOT NULL", "rel.season IS NOT NULL"]
    if teams:
        relationship_predicates.append("rel.team IN $teams")
    if start_year is not None:
        relationship_predicates.append("rel.season >= $start_year")
    if end_year is not None:
        relationship_predicates.append("rel.season <= $end_year")

    path_filter = ""
    if relationship_predicates:
        path_filter = f" AND all(rel IN relationships(path) WHERE {' AND '.join(relationship_predicates)})"

    query = """
        MATCH (start:Player {id: $start_player_id})
        CALL apoc.path.expandConfig(start, {
            relationshipFilter: $rel_filter,
            minLevel: $min_hops,
            maxLevel: $max_hops,
            bfs: true,
            uniqueness: 'NODE_GLOBAL',
            filterStartNode: true,
            limit: $sample_limit
        })
        YIELD path
        WITH path, last(nodes(path)) AS end
        WHERE end.fullName IS NOT NULL AND end.id <> $start_player_id
    """
    query += path_filter
    query += """
        WITH DISTINCT end
        ORDER BY rand()
        LIMIT 1
        RETURN end.id AS id, end.fullName AS full_name
    """

    params = {
        "start_player_id": start_player_id,
        "rel_filter": rel_filter,
        "min_hops": min_hops,
        "max_hops": max_hops,
        "sample_limit": sample_limit,
    }
    if teams:
        params["teams"] = [team.upper() for team in teams]
    if start_year is not None:
        params["start_year"] = _year_to_season(start_year)
    if end_year is not None:
        params["end_year"] = _year_to_season(end_year)

    logger.info(
        "Connected-player lookup start player=%s hops=%s..%s sample_limit=%s rel_types=%s",
        start_player_id,
        min_hops,
        max_hops,
        sample_limit,
        rel_types,
    )

    result = await db.run_query(query, params)
    logger.info(
        "Connected-player lookup finished player=%s result_count=%s elapsed=%.3fs",
        start_player_id,
        len(result),
        time.perf_counter() - started,
    )

    if not result:
        return None
    return {"id": result[0]["id"], "full_name": result[0]["full_name"]}


async def find_shortest_path_for_game(
    player1_id: int,
    player2_id: int,
    teams: Optional[List[str]] = None,
    start_year: Optional[int] = None,
    end_year: Optional[int] = None,
    game_types: Optional[List[str]] = None,
    max_hops: int = 6,
) -> List[Dict[str, Any]]:
    """
    Bounded shortest path for game mode with optional relationship filters.
    Uses in-process BFS to avoid APOC heap blowups on dense filtered graphs.
    """
    bounded_hops = max(1, int(max_hops))
    max_visited_nodes = 40000

    if player1_id == player2_id:
        name = await get_name_from_playerid(player1_id)
        return [{"id": player1_id, "full_name": name}] if name else []

    start_name, end_name = await asyncio.gather(
        get_name_from_playerid(player1_id),
        get_name_from_playerid(player2_id),
    )
    if not start_name or not end_name:
        return []

    queue = deque([(int(player1_id), 0)])
    parent_by_node: Dict[int, Optional[int]] = {int(player1_id): None}
    name_by_node: Dict[int, str] = {
        int(player1_id): start_name,
        int(player2_id): end_name,
    }

    while queue:
        current_id, depth = queue.popleft()
        if depth >= bounded_hops:
            continue

        neighbors = await get_teammates_of_player_with_options(
            playerid=current_id,
            teams=teams,
            start_year=start_year,
            end_year=end_year,
            game_types=game_types,
        )

        for neighbor in neighbors:
            neighbor_id = int(neighbor["id"])
            if neighbor_id in parent_by_node:
                continue

            parent_by_node[neighbor_id] = current_id
            neighbor_name = neighbor.get("full_name")
            if isinstance(neighbor_name, str) and neighbor_name:
                name_by_node[neighbor_id] = neighbor_name

            if len(parent_by_node) > max_visited_nodes:
                logger.warning(
                    "Aborting shortest-path BFS p1=%s p2=%s visited_nodes>%s",
                    player1_id,
                    player2_id,
                    max_visited_nodes,
                )
                return []

            if neighbor_id == int(player2_id):
                path_ids: List[int] = []
                cursor: Optional[int] = neighbor_id
                while cursor is not None:
                    path_ids.append(cursor)
                    cursor = parent_by_node[cursor]
                path_ids.reverse()

                resolved_path: List[Dict[str, Any]] = []
                for path_id in path_ids:
                    full_name = name_by_node.get(path_id)
                    if not full_name:
                        full_name = await get_name_from_playerid(path_id) or str(path_id)
                    resolved_path.append({"id": path_id, "full_name": full_name})
                return resolved_path

            queue.append((neighbor_id, depth + 1))

    return []
