import psycopg2
from psycopg2 import Error
from neo4j import Driver, GraphDatabase, Session
import os
from dotenv import load_dotenv

def connect_to_postgres() -> psycopg2.extensions.connection | None:
    load_dotenv()
    POSTGRES_USER = os.getenv("POSTGRES_USER")
    POSTGRES_PASS = os.getenv("POSTGRES_PASS")

    connection = None

    try:
        # 1. Connect to the PostgreSQL database
        connection = psycopg2.connect(
            host="localhost",          # Or your database server IP
            database="nhlptphockeydata",
            user=POSTGRES_USER,
            password=POSTGRES_PASS,
            port="5432"                # Default PostgreSQL port
        )

        # # 2. Create a cursor object to execute SQL commands
        # with connection.cursor() as cursor:
        #     # Example: Fetching the database version
        #     cursor.execute("SELECT version();")
        #     db_version = cursor.fetchone()
        #     print(f"Connected to PostgreSQL! Version: {db_version}\n")

        #     # Example: Querying data from a table
        #     cursor.execute("SELECT * FROM your_table_name LIMIT 5;")
        #     records = cursor.fetchall()
            
        #     print("Displaying rows:")
        #     for row in records:
        #         print(row)

    except (Exception, Error) as error:
        print(f"Error while connecting to PostgreSQL: {error}")
        connection = None  # Ensure connection is None if there's an error

    return connection

def close_postgres_connection(connection: psycopg2.extensions.connection):
    """Closes the PostgreSQL connection."""
    if connection:
        connection.close()
        print("\nPostgreSQL connection is closed.")
    else:
        print("No active PostgreSQL connection to close.")

def connect_to_neo4j() -> Driver:
    """Connects to the Neo4j database."""
    load_dotenv()
    NEO4J_URI = os.getenv("NEO4J_URI")
    NEO4J_USER = os.getenv("NEO4J_USER")
    NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
    if not NEO4J_URI or not NEO4J_USER or not NEO4J_PASSWORD:
        raise ValueError("Neo4j connection details are missing in the environment variables.")
    driver: Driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))  # pyright: ignore[reportUnknownMemberType]
    driver.verify_connectivity()  # pyright: ignore[reportUnknownMemberType]
    return driver

def close_neo4j_session(session: Session):
    """Closes the Neo4j session."""
    if session:
        session.close()
        print("Neo4j session is closed.")
    else:
        print("No active Neo4j session to close.")

def close_neo4j_connection(driver: Driver):
    """Closes the Neo4j connection."""
    if driver:
        driver.close()
        print("Neo4j connection is closed.")
    else:
        print("No active Neo4j connection to close.")
