import asyncio
import httpx
import sys
from typing import Dict, Any, List
from backend.db import session
from backend.data_pipeline import sources

# RUN THIS BEFORE RUNNING PIPELINE
# export PYTHONPATH="/home/jgilland/dev/NHLPlayerToPlayer/:$PYTHONPATH"

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

def clear_database():
    """Deletes all nodes and relationships from the Neo4j database."""
    print("--- Clearing the entire Neo4j database ---")
    db = session.get_graph_db()
    db.run_query("MATCH (n) DETACH DELETE n")
    print("Database cleared successfully.")


async def main():
    """
    Main function to run the data pipeline.
    """
    # Get a database session
    db = session.get_graph_db()

    # For this example, we'll process the 2024-2025 season.
    # You can easily loop through multiple seasons here.
    seasons_to_process = [2024]

    async with httpx.AsyncClient() as client:
        for season in seasons_to_process:
            print(f"--- Processing season {season}-{season+1} ---")
            game_ids = await sources.get_all_game_ids_for_season(client, season)
            print(f"Found {len(game_ids)} games for the season.")

            for game_id in game_ids:
                game_data = await sources.fetch_game_boxscore(client, game_id)

                if not game_data:
                    continue

                # FIX: Check for the existence of player stats to prevent KeyErrors.
                if 'playerByGameStats' not in game_data or not game_data.get('playerByGameStats'):
                    print(f"Skipping game {game_id}: Missing or empty 'playerByGameStats' data.")
                    continue

                # 1. Extract all unique player IDs from the game.
                home_player_ids = _extract_player_ids_from_roster(game_data['playerByGameStats']['homeTeam'])
                away_player_ids = _extract_player_ids_from_roster(game_data['playerByGameStats']['awayTeam'])
                all_player_ids_in_game = list(set(home_player_ids + away_player_ids))

                if not all_player_ids_in_game:
                    continue

                # 2. Check which players already have a full name in the graph.
                records = db.run_query(
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

                if ids_to_fetch:
                    tasks = [sources.fetch_player_landing(client, pid) for pid in ids_to_fetch]
                    player_landings = await asyncio.gather(*tasks)

                    players_to_update = []
                    for landing_data in player_landings:
                        if landing_data and 'firstName' in landing_data:
                            players_to_update.append({
                                "id": landing_data['playerId'],
                                "fullName": f"{landing_data['firstName']['default']} {landing_data['lastName']['default']}"
                            })
                    
                    # 4. Update the graph with the new full names.
                    if players_to_update:
                        db.run_query(
                            """
                            UNWIND $players as player_data
                            MERGE (p:Player {id: player_data.id})
                            SET p.fullName = player_data.fullName
                            """,
                            parameters={"players": players_to_update}
                        )

                # 5. Create teammate relationships based on game type.
                rel_type = _get_relationship_type_from_game_id(game_id)

                # The relationship type (e.g., TEAMMATE_IN_REGULAR_SEASON) is now dynamic.
                teammate_query = f"""
                    UNWIND $player_ids as p1_id
                    UNWIND $player_ids as p2_id
                    WITH p1_id, p2_id WHERE p1_id < p2_id
                    MATCH (p1:Player {{id: p1_id}}), (p2:Player {{id: p2_id}})
                    MERGE (p1)-[:{rel_type} {{gameId: $game_id, season: $season, team: $tricode}}]-(p2)
                """

                # Run for home team
                db.run_query(teammate_query, parameters={
                    "player_ids": home_player_ids,
                    "game_id": game_id,
                    "season": game_data['season'],
                    "tricode": game_data['homeTeam']['abbrev']
                })

                # Run for away team
                db.run_query(teammate_query, parameters={
                    "player_ids": away_player_ids,
                    "game_id": game_id,
                    "season": game_data['season'],
                    "tricode": game_data['awayTeam']['abbrev']
                })

                print(f"Processed game {game_id} for graph.")

if __name__ == "__main__":
    if "--clear" in sys.argv:
        clear_database()
    else:
        asyncio.run(main())