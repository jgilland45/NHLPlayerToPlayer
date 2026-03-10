import asyncio
import argparse
import httpx
import sys
from collections import Counter
import logging
from typing import Dict, Any, List
from backend.db import session
from backend.data_pipeline import sources

# --- Setup Logging ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)

def _extract_player_ids_from_roster(roster: Dict[str, Any]) -> List[int]:
    """Extracts all player IDs from a team's roster in the boxscore."""
    player_ids = []
    for position in ['forwards', 'defense', 'goalies']:
        for p in roster.get(position, []):
            player_ids.append(p['playerId'])
    return player_ids

def _get_relationship_type_from_game_id(game_id: int) -> str:
    """Determines the Neo4j relationship type based on the NHL game ID."""
    # Game ID format is YYYYTTNNNN, where TT is the game type.
    game_type_code = (game_id // 10000) % 100

    # This mapping converts the numeric game type code from the API
    # into a descriptive relationship type for the graph.
    # Game type 13 (cancelled games) is intentionally omitted.
    type_mapping = {
        1: "TEAMMATE_IN_PRE_SEASON",
        2: "TEAMMATE_IN_REGULAR_SEASON",
        3: "TEAMMATE_IN_PLAYOFFS",
        4: "TEAMMATE_IN_ALL_STAR",
        6: "TEAMMATE_IN_WORLD_CUP_GROUP",
        7: "TEAMMATE_IN_WORLD_CUP_KNOCKOUT",
        8: "TEAMMATE_IN_WORLD_CUP_EXHIBITION",
        9: "TEAMMATE_IN_OLYMPICS",
        10: "TEAMMATE_IN_YOUNG_STARS",
        12: "TEAMMATE_IN_SPECIAL_EVENT",
        14: "TEAMMATE_IN_CANADA_CUP",
        18: "TEAMMATE_IN_EXHIBITION",
        19: "TEAMMATE_IN_FOUR_NATIONS",
    }

    # Default to a generic type if the code is unknown
    return type_mapping.get(game_type_code, "TEAMMATE_IN_OTHER")

async def create_indexes():
    """
    Creates necessary indexes in the Neo4j database for query performance.
    This is an idempotent operation; if indexes already exist, it does nothing.
    """
    logger.info("--- Ensuring database indexes are created ---")
    db = session.get_graph_db()

    # Enforce canonical player identity. This also creates the backing index.
    # If this fails, the graph currently has duplicate Player.id values that must be deduplicated.
    try:
        await db.run_query(
            "CREATE CONSTRAINT player_id_unique IF NOT EXISTS FOR (p:Player) REQUIRE p.id IS UNIQUE"
        )
    except Exception:
        logger.error(
            "Failed creating player_id_unique constraint. Resolve duplicate Player.id nodes first, then rerun --create-indexes.",
            exc_info=True,
        )
        raise

    # To get all possible relationship types, we can inspect the mapping
    # dictionary in the `_get_relationship_type_from_game_id` function.
    all_rel_types = set(_get_relationship_type_from_game_id(g) for g in range(1, 20))
    all_rel_types.add("TEAMMATE_IN_OTHER") # Add the default

    # Create composite indexes on (season, team) for each relationship type.
    # This will dramatically speed up filtering by year and team.
    index_creation_tasks = []
    for rel_type in all_rel_types:
        # Neo4j index names must be unique. We'll generate one per type.
        index_name = f"rel_{rel_type}_season_team_idx"
        query = f"""
        CREATE RANGE INDEX {index_name} IF NOT EXISTS
        FOR ()-[r:{rel_type}]-() ON (r.season, r.team)
        """
        index_creation_tasks.append(db.run_query(query))

    try:
        await asyncio.gather(*index_creation_tasks)
        logger.info("All necessary indexes have been created or already exist.")
    except Exception as e:
        logger.error("An error occurred during index creation.", exc_info=True)
        raise

async def clear_database():
    """Deletes all nodes and relationships from the Neo4j database."""
    logger.info("--- Clearing the entire Neo4j database ---")
    db = session.get_graph_db()

    # Phase 1: delete relationships first. This avoids high-memory DETACH operations.
    rel_batch_size = 1000
    total_relationships_deleted = 0

    while True:
        result = await db.run_query(
            """
            MATCH ()-[r]-()
            WITH r LIMIT $batch_size
            DELETE r
            RETURN count(r) AS deleted
            """,
            parameters={"batch_size": rel_batch_size},
        )

        deleted = int(result[0]["deleted"]) if result else 0
        total_relationships_deleted += deleted

        if deleted == 0:
            break

        logger.info("Deleted %s relationships so far...", total_relationships_deleted)

    # Phase 2: delete remaining isolated nodes.
    node_batch_size = 5000
    total_nodes_deleted = 0

    while True:
        result = await db.run_query(
            """
            MATCH (n)
            WITH n LIMIT $batch_size
            DELETE n
            RETURN count(n) AS deleted
            """,
            parameters={"batch_size": node_batch_size},
        )

        deleted = int(result[0]["deleted"]) if result else 0
        total_nodes_deleted += deleted

        if deleted == 0:
            break

        logger.info("Deleted %s nodes so far...", total_nodes_deleted)

    logger.info(
        "Deleted %s relationships and %s nodes in total.",
        total_relationships_deleted,
        total_nodes_deleted,
    )
    logger.info("Database cleared successfully.")

async def get_existing_game_ids(db: session.GraphDB) -> set[int]:
    """Queries the database to find which games have already been processed."""
    query = """
    MATCH ()-[r]->()
    WHERE r.gameId IS NOT NULL
    RETURN DISTINCT r.gameId AS gameId
    """
    result = await db.run_query(query)
    return {record["gameId"] for record in result if record["gameId"] is not None}

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Populate NHL teammate graph data into Neo4j.")
    parser.add_argument("--clear", action="store_true", help="Delete all nodes and relationships from Neo4j.")
    parser.add_argument("--create-indexes", action="store_true", help="Create Neo4j indexes for faster querying.")
    parser.add_argument(
        "--start-season",
        type=int,
        default=1917,
        help="First season year to query (e.g., 2018 means 2018-19 season). Default: 1917.",
    )
    parser.add_argument(
        "--end-season",
        type=int,
        default=2024,
        help="Last season year to query (inclusive). Default: 2024.",
    )
    parser.add_argument(
        "--max-games",
        type=int,
        default=None,
        help="Optional cap on number of games to process after diffing against existing DB.",
    )
    parser.add_argument(
        "--latest-first",
        action="store_true",
        help="Process newer game IDs first (recommended for quick partial loads).",
    )
    return parser.parse_args()

async def main(args: argparse.Namespace):
    """
    Main function to run the data pipeline. It fetches all possible game IDs,
    compares them against games already in the database, and processes only
    the missing ones. This makes the pipeline fully idempotent at the game level.
    """
    db = session.get_graph_db()

    async with httpx.AsyncClient() as client:
        # 1. Get all game IDs that are already in the database.
        logger.info("Checking for games already in the database...")
        existing_game_ids = await get_existing_game_ids(db)
        logger.info(f"Found {len(existing_game_ids)} games already processed.")

        if args.start_season > args.end_season:
            raise ValueError("--start-season cannot be greater than --end-season")

        # 2. Fetch all game IDs for the requested seasons from the NHL API.
        all_possible_seasons = range(args.start_season, args.end_season + 1)
        logger.info(f"Fetching all game IDs for seasons {all_possible_seasons.start} to {all_possible_seasons.stop - 1}...")
        
        season_id_tasks = [sources.get_all_game_ids_for_season(client, season) for season in all_possible_seasons]
        list_of_game_id_lists = await asyncio.gather(*season_id_tasks)
        
        all_api_game_ids = {game_id for sublist in list_of_game_id_lists for game_id in sublist}
        logger.info(f"Found a total of {len(all_api_game_ids)} possible games from the API.")

        # 3. Determine which games need to be processed.
        game_ids_to_process = sorted(
            (Counter(all_api_game_ids) - Counter(existing_game_ids)).elements(),
            reverse=args.latest_first,
        )

        if args.max_games is not None:
            if args.max_games <= 0:
                raise ValueError("--max-games must be greater than 0")
            game_ids_to_process = game_ids_to_process[:args.max_games]

        if not game_ids_to_process:
            logger.info("All games are up to date. No new data to process.")
            return

        logger.info(f"Found {len(game_ids_to_process)} new games to process.")
        logger.info(f"Sample of games to process: {game_ids_to_process[:20]}")

        # 4. Process all missing games concurrently.
        semaphore = asyncio.Semaphore(25)
        game_tasks = [process_game(client, db, game_id, semaphore) for game_id in game_ids_to_process]
        await asyncio.gather(*game_tasks)

def _update_graph_for_game_unit_of_work(tx, all_player_ids, players_to_update, game_data, home_player_ids, away_player_ids, game_id, rel_type):
    """
    A single, atomic unit of work to update the graph for one game.
    This function is executed within a managed, auto-retrying transaction.
    """
    # 1. Establish locks on ALL players in the game in a canonical order.
    # This is the key to preventing deadlocks. We MERGE every player
    # involved in the game to acquire locks in a sorted order, even if we
    # don't need to update their names. This ensures that any two concurrent
    # transactions touching the same players will lock them in the same order.
    all_player_ids.sort()
    tx.run(
        """
        UNWIND $player_ids as p_id
        MERGE (p:Player {id: p_id})
        // Force a write lock on each node to prevent deadlocks.
        // By setting a property, we ensure an ExclusiveLock is taken,
        // and because we process players sorted by ID, we do this
        // in a canonical order.
        SET p._lock = timestamp()
        """,
        player_ids=all_player_ids
    )

    # 2. Update names for the players that need it.
    if players_to_update:
        # Sorting here is technically redundant since all_player_ids is a sorted
        # superset, but it's harmless and good practice for function isolation.
        players_to_update.sort(key=lambda p: p['id'])
        tx.run(
            """
            UNWIND $players as player_data
            MATCH (p:Player {id: player_data.id})
            SET p.fullName = player_data.fullName
            """,
            players=players_to_update
        )

    # 3. Create teammate relationships
    # The relationship type (e.g., TEAMMATE_IN_REGULAR_SEASON) is now dynamic.
    teammate_query = f"""
        UNWIND $player_ids as p1_id
        UNWIND $player_ids as p2_id
        WITH p1_id, p2_id WHERE p1_id < p2_id
        MATCH (p1:Player {{id: p1_id}}), (p2:Player {{id: p2_id}})
        MERGE (p1)-[:{rel_type} {{gameId: $game_id, season: $season, team: $tricode}}]-(p2)
    """

    home_player_ids.sort()
    away_player_ids.sort()

    tx.run(teammate_query,
           player_ids=home_player_ids,
           game_id=game_id,
           season=game_data['season'],
           tricode=game_data['homeTeam']['abbrev'])

    tx.run(teammate_query,
           player_ids=away_player_ids,
           game_id=game_id,
           season=game_data['season'],
           tricode=game_data['awayTeam']['abbrev'])

async def process_game(client: httpx.AsyncClient, db: session.GraphDB, game_id: int, semaphore: asyncio.Semaphore):
    """
    Process a single game, fetching data and updating the graph.
    """
    async with semaphore:
        game_data = await sources.fetch_game_boxscore(client, game_id)

        if not game_data:
            return

        # FIX: Check for the existence of player stats to prevent KeyErrors.
        if 'playerByGameStats' not in game_data or not game_data.get('playerByGameStats'):
            logger.warning(f"Skipping game {game_id}: Missing or empty 'playerByGameStats' data.")
            return

        # 1. Extract all unique player IDs from the game.
        home_player_ids = _extract_player_ids_from_roster(game_data['playerByGameStats']['homeTeam'])
        away_player_ids = _extract_player_ids_from_roster(game_data['playerByGameStats']['awayTeam'])
        all_player_ids_in_game = list(set(home_player_ids + away_player_ids))

        if not all_player_ids_in_game:
            return

        # 2. Check which players already have a full name in the graph.
        records = await db.run_query(
            """
            UNWIND $player_ids as p_id
            MATCH (p:Player {id: p_id})
            WHERE p.fullName IS NOT NULL
            RETURN p.id
            """,
            parameters={"player_ids": all_player_ids_in_game}
        )
        existing_player_ids = {record['p.id'] for record in records}

        # 3. For any players missing a full name, fetch their details.
        ids_to_fetch = [pid for pid in all_player_ids_in_game if pid not in existing_player_ids]

        players_to_update = []
        if ids_to_fetch:
            tasks = [sources.fetch_player_landing(client, pid) for pid in ids_to_fetch]
            player_landings = await asyncio.gather(*tasks)

            for landing_data in player_landings:
                if landing_data and 'firstName' in landing_data:
                    players_to_update.append({
                        "id": landing_data['playerId'],
                        "fullName": f"{landing_data['firstName']['default']} {landing_data['lastName']['default']}"
                    })
        
        rel_type = _get_relationship_type_from_game_id(game_id)

        # 4. Atomically update the graph for this game.
        # This must run for every game to create relationships, even if no player names needed updating.
        await db.run_unit_of_work(
            _update_graph_for_game_unit_of_work,
            all_player_ids=all_player_ids_in_game,
            players_to_update=players_to_update,
            game_data=game_data,
            home_player_ids=home_player_ids,
            away_player_ids=away_player_ids,
            game_id=game_id,
            rel_type=rel_type
        )

        logger.info(f"Processed game {game_id} for graph.")

if __name__ == "__main__":
    try:
        args = parse_args()

        if args.clear:
            asyncio.run(clear_database())
        elif args.create_indexes:
            asyncio.run(create_indexes())
        else:
            asyncio.run(main(args))
        logger.info("Pipeline finished successfully.")
    except Exception as e:
        logger.critical("Pipeline failed with an unhandled exception.", exc_info=True)
        sys.exit(1)