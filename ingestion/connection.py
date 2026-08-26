import psycopg2
from psycopg2 import Error
import os
from dotenv import load_dotenv

POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASS = os.getenv("POSTGRES_PASS")

def connect_to_postgres() -> psycopg2.extensions.connection | None:
    load_dotenv()

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

        # 2. Create a cursor object to execute SQL commands
        with connection.cursor() as cursor:
            # Example: Fetching the database version
            cursor.execute("SELECT version();")
            db_version = cursor.fetchone()
            print(f"Connected to PostgreSQL! Version: {db_version}\n")

            # Example: Querying data from a table
            cursor.execute("SELECT * FROM your_table_name LIMIT 5;")
            records = cursor.fetchall()
            
            print("Displaying rows:")
            for row in records:
                print(row)

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
