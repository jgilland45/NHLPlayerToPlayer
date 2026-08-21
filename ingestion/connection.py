import psycopg2
from psycopg2 import Error
import os
from dotenv import load_dotenv


load_dotenv()

POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASS = os.getenv("POSTGRES_PASS")

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

        # # Example: Querying data from a table
        # cursor.execute("SELECT * FROM your_table_name LIMIT 5;")
        # records = cursor.fetchall()
        
        # print("Displaying rows:")
        # for row in records:
        #     print(row)

except (Exception, Error) as error:
    print(f"Error while connecting to PostgreSQL: {error}")

finally:
    # 3. Clean up and close the connection pool
    if 'connection' in locals() and connection:
        connection.close()
        print("\nPostgreSQL connection is closed.")
