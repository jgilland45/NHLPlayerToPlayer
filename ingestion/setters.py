# This file is for setting data into databases (both postgres and neo4j).
# This should only include functions that are used to set data. No data transformation should be done here.

import psycopg2
from neo4j import Driver, ResultSummary

import datatypes

# Keep transactions bounded when importing a full season of games.
NEO4J_RELATIONSHIP_BATCH_SIZE = 1_000

# POSTGRES SETTERS

def save_teams_to_postgres(connection: psycopg2.extensions.connection, teams: list[datatypes.DBTeams]):
    """
    Save a list of DBTeam objects into the PostgreSQL database.
    """
    with connection.cursor() as cursor:
        for team in teams:
            cursor.execute(
                """
                INSERT INTO teams (team_id, name, abbreviation)
                VALUES (%s, %s, %s)
                ON CONFLICT (team_id) DO NOTHING;
                """,
                (
                    team.teamId,
                    team.teamName,
                    team.teamAbbrev,
                ),
            )

def save_players_to_postgres(connection: psycopg2.extensions.connection, players: list[datatypes.DBPlayer]):
    """
    Save a list of DBPlayer objects into the PostgreSQL database.
    """
    with connection.cursor() as cursor:
        for player in players:
            cursor.execute(
                """
                INSERT INTO players (
                player_id,
                name,
                position_code,
                active,
                height,
                height_in_inches,
                height_in_centimeters,
                weight_in_pounds,
                weight_in_kilograms,
                birth_city,
                birth_state_province,
                birth_country,
                current_team_id,
                current_team_abbreviation,
                last_team_id,
                last_team_abbreviation,
                last_season_id,
                sweater_number
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (player_id) DO NOTHING;
                """,
                (
                    player.playerId,
                    player.name,
                    player.positionCode,
                    player.active,
                    player.height,
                    player.heightInInches,
                    player.heightInCentimeters,
                    player.weightInPounds,
                    player.weightInKilograms,
                    player.birthCity,
                    player.birthStateProvince,
                    player.birthCountry,
                    player.teamId,
                    player.teamAbbrev,
                    player.lastTeamId,
                    player.lastTeamAbbrev,
                    player.lastSeasonId,
                    player.sweaterNumber
                ),
            )

def save_games_to_postgres(connection: psycopg2.extensions.connection, games: list[datatypes.DBGame]):
    """
    Save a list of DBGame objects into the PostgreSQL database.
    """
    with connection.cursor() as cursor:
        for game in games:
            cursor.execute(
                """
                INSERT INTO games (
                game_id,
                season,
                game_type,
                eastern_start_time,
                game_date,
                game_number,
                game_schedule_state_id,
                game_state_id,
                home_score,
                home_team_id,
                visiting_score,
                visiting_team_id,
                period
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (game_id) DO NOTHING;
                """,
                (
                    game.id,
                    game.season,
                    getattr(game.gameType, "value", game.gameType),
                    game.easternStartTime,
                    game.gameDate,
                    game.gameNumber,
                    game.gameScheduleStateId,
                    game.gameStateId,
                    game.homeScore,
                    game.homeTeamId,
                    game.visitingScore,
                    game.visitingTeamId,
                    game.period,
                ),
            )


def save_game_players_to_postgres(connection: psycopg2.extensions.connection, game_storage_list: list[datatypes.GameStorage]):
    """
    Save a list of GameStorage objects into the PostgreSQL database.
    """
    with connection.cursor() as cursor:
        for game_storage in game_storage_list:
            cursor.execute(
                """
                INSERT INTO game_players (
                game_id,
                season,
                player_id,
                game_type,
                team_id
                )
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (game_id, player_id) DO NOTHING;
                """,
                (
                    game_storage.gameId,
                    game_storage.season,
                    game_storage.playerId,
                    getattr(game_storage.gameType, "value", game_storage.gameType),
                    game_storage.teamId,
                ),
            )

# NEO4J SETTERS

def save_teammate_relationships_to_neo4j(driver: Driver, teammate_relationships: list[datatypes.TeammateRelationship]):
    """
    Save a list of TeammateRelationship objects into the Neo4j database.
    """
    query = """
        UNWIND $relationships AS relationship
        MERGE (a:Player {id: relationship.player1Id})
        MERGE (b:Player {id: relationship.player2Id})
        MERGE (a)-[r:TEAMMATE {
            teamId: relationship.teamId,
            season: relationship.season,
            gameType: relationship.gameType
        }]->(b)
    """

    summaries: list[ResultSummary] = []
    for start in range(0, len(teammate_relationships), NEO4J_RELATIONSHIP_BATCH_SIZE):
        batch = teammate_relationships[start:start + NEO4J_RELATIONSHIP_BATCH_SIZE]
        summary = driver.execute_query(query, {"relationships": [
            {
                **relationship.__dict__,
                "gameType": relationship.gameType.value,
            }
            for relationship in batch
        ]}).summary
        summaries.append(summary)

    print(f"""
        Saved {len(teammate_relationships)} teammate relationships to Neo4j.
        Completed {len(summaries)} transaction(s).
    """)