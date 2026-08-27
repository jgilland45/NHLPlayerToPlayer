# This file is for setting data into databases (both postgres and neo4j).
# This should only include functions that are used to set data. No data transformation should be done here.

def load_teams_to_postgres(teams, conn):
    """
    Load teams into postgres database.
    :param teams: list of team dictionaries
    :param conn: psycopg2 connection object
    """
    with conn.cursor() as cur:
        for team in teams:
            cur.execute(
                """
                INSERT INTO teams (id, name, abbreviation, conference, division)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING;
                """,
                (team['id'], team['name'], team['abbreviation'], team['conference'], team['division'])
            )
    conn.commit()