# Migration Plan: From Relational to Graph Database

This document outlines a strategic plan to migrate your application's backend from a traditional relational database (SQLite) to a modern graph database (Neo4j). This move will dramatically simplify your code, unlock powerful new query capabilities, and align your database structure with the natural "connectedness" of your data.

---

## Why a Graph Database? The "Aha!" Moment

Your application is fundamentally about **relationships**: which players were teammates, what teams they played for, and how they are all connected. While you've successfully modeled this in SQLite, you're likely noticing that the queries to uncover these relationships are getting complex. 

Consider how you find a player's teammates right now:

```sql
-- Find all teammates for a given player
SELECT DISTINCT(pg2.playerid)
FROM Player_Game pg1, Player_Game pg2
WHERE LOWER(pg1.playerid) = LOWER(?)
  AND pg1.gameid = pg2.gameid
  AND pg1.teamid = pg2.teamid;
```

This requires a "self-join" on the `Player_Game` table, which can be inefficient and hard to read. You're essentially telling the database to scan the same large table twice to find matching `gameid` and `teamid` values.

**Now, imagine it in a graph.**

Your data isn't a set of tables; it's a network. Players are *nodes*, and the fact that they played together is a *relationship* (an edge) connecting them.

<img src="https://dist.neo4j.com/wp-content/uploads/20180424153437/graph-model-for-recommendation-engine-700x394.png" alt="Graph Model Example" width="600"/>

In a graph, the query to find teammates becomes incredibly simple and intuitive:

> "Start at one player's node, follow the 'TEAMMATE' relationship, and tell me what players you find."

This is not only easier to write but is also how graph databases are optimized to work, making these queries incredibly fast, even with millions of relationships.

**The core benefit:** You can ask complex questions about connections that are extremely difficult (or impossible) to ask with SQL, like "Find the shortest path of teammates connecting Sidney Crosby to Wayne Gretzky."

For this migration, we will use **Neo4j**, the most popular and mature graph database available, which has excellent Python support.

---

## The Migration Plan: A Step-by-Step Guide

Here is a detailed, actionable plan to transition your backend.

### Step 1: Set Up Your Neo4j Database

The easiest way to get a Neo4j instance running locally is with Docker. It's a single command and keeps the installation isolated.

1.  **Install Docker:** If you don't have it, get it from the [official Docker website](https://www.docker.com/products/docker-desktop/).

2.  **Run Neo4j:** Open your terminal and run the following command. This will download the Neo4j image and start a container.

    ```bash
    docker run \
        --name nhl-graph-db \
        -p 7474:7474 -p 7687:7687 \
        -d \
        -e NEO4J_AUTH=neo4j/a-super-secret-password \
        neo4j:latest
    ```

3.  **Access the Neo4j Browser:** Once it's running, open your web browser and go to `http://localhost:7474`. This is a powerful UI for interacting with your database. Log in with the username `neo4j` and the password `a-super-secret-password` that you set in the command above.

    *   The database itself is accessible to your application via the **Bolt protocol** at `bolt://localhost:7687`.

### Step 2: Connect Your Python App to Neo4j

Now, let's get your FastAPI application talking to Neo4j.

1.  **Add the Neo4j Driver:** The official Python driver is the bridge between your code and the database. Add it to your `backend/requirements.txt`:

    ```
    # backend/requirements.txt
    fastapi
    uvicorn
    requests
    sqlalchemy
    pydantic-settings
    httpx
    redis
    neo4j
    ```

2.  **Install the Driver:** Run the installation command using your virtual environment's pip.

    ```bash
    /home/jgilland/dev/NHLPlayerToPlayer/.venv/bin/pip install neo4j
    ```

3.  **Update Configuration:** Add the Neo4j connection details to your settings file.

    ```python
    # backend/core/config.py
    class Settings(BaseSettings):
        # ... existing settings

        # Neo4j Database
        NEO4J_URI: str = "bolt://localhost:7687"
        NEO4J_USER: str = "neo4j"
        NEO4J_PASSWORD: str = "a-super-secret-password"

        model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8')

    settings = Settings()
    ```

4.  **Create a Graph Session Manager:** Just like you have `session.py` for SQLAlchemy, you need a file to manage the Neo4j driver instance. Create `backend/db/graph_session.py`:

    ```python
    # backend/db/graph_session.py
    from neo4j import GraphDatabase
    from backend.core.config import settings

    class GraphDB:
        def __init__(self, uri, user, password):
            self._driver = GraphDatabase.driver(uri, auth=(user, password))

        def close(self):
            self._driver.close()

        def run_query(self, query, parameters=None):
            with self._driver.session() as session:
                result = session.run(query, parameters)
                return [record for record in result]

    # Create a single, importable instance of the graph database connection
    graph_db = GraphDB(
        uri=settings.NEO4J_URI,
        user=settings.NEO4J_USER,
        password=settings.NEO4J_PASSWORD
    )

    # Dependency for FastAPI
    def get_graph_db():
        return graph_db
    ```

### Step 3: Redefine and Load Your Data Model

This is where you translate your tables and rows into nodes and relationships. We will use the Cypher query language to do this.

1.  **The Graph Model:**
    *   **Nodes:** We'll have one primary node type: `Player`.
        *   `(:Player {id: 8471234, fullName: 'Sidney Crosby'})`
    *   **Relationships:** The core of the app is the `TEAMMATE` relationship. We can add properties to it, like the season and team.
        *   `(:Player)-[:TEAMMATE_IN {season: 2023, team: 'PIT'}]->(:Player)`

2.  **Refactor the Data Pipeline:** Update `backend/data_pipeline/run_pipeline.py` to populate the graph.

    Your new pipeline will fetch game data as before, but instead of inserting into SQLite, it will execute Cypher queries.

    ```python
    # backend/data_pipeline/run_pipeline.py (New Version)
    import asyncio
    import httpx
    from backend.db.graph_session import graph_db
    from backend.data_pipeline import sources

    async def main():
        game_ids = await sources.get_all_game_ids_for_season(2023)

        async with httpx.AsyncClient() as client:
            for game_id in game_ids:
                game_data = await sources.fetch_game_boxscore(client, game_id)
                if not game_data: continue

                # 1. Create/update all players in the game
                players_in_game = extract_players_from_gamedata(game_data)
                graph_db.run_query(
                    """ 
                    UNWIND $players as player_data
                    MERGE (p:Player {id: player_data.id})
                    ON CREATE SET p.fullName = player_data.fullName
                    """,
                    parameters={"players": players_in_game}
                )

                # 2. Create TEAMMATE relationships
                home_team_ids = [p['id'] for p in players_in_game if p['team'] == 'home']
                away_team_ids = [p['id'] for p in players_in_game if p['team'] == 'away']
                
                # Connect all home players to each other
                graph_db.run_query(
                    """
                    UNWIND $player_ids as p1_id
                    UNWIND $player_ids as p2_id
                    WITH p1_id, p2_id WHERE p1_id < p2_id
                    MATCH (p1:Player {id: p1_id}), (p2:Player {id: p2_id})
                    MERGE (p1)-[r:TEAMMATE_IN {season: $season, team: $tricode}]-(p2)
                    """,
                    parameters={
                        "player_ids": home_team_ids,
                        "season": game_data['season'],
                        "tricode": game_data['homeTeam']['abbrev']
                    }
                )
                # ... (repeat for away team)

                print(f"Processed game {game_id} for graph.")

        graph_db.close()

    # (You would need to implement extract_players_from_gamedata)

    if __name__ == "__main__":
        asyncio.run(main())
    ```

### Step 4: Refactor the API to Query the Graph

This is the payoff. Your complex SQL queries become simple, elegant Cypher queries.

1.  **Create `backend/db/graph_crud.py`:** This will hold your data-access functions.

2.  **Example 1: Get All Teammates**

    ```python
    # backend/db/graph_crud.py
    from backend.db.graph_session import graph_db

    def get_teammates_for_player(player_id: int):
        query = """
        MATCH (p1:Player {id: $player_id})-[:TEAMMATE_IN]-(p2:Player)
        RETURN DISTINCT p2.id as id, p2.fullName as fullName
        """
        results = graph_db.run_query(query, {"player_id": player_id})
        return [dict(record) for record in results]
    ```

3.  **Example 2: The "Player-to-Player" Connection Path (The Holy Grail)**

    This is where the graph model shines. Finding the shortest connection path between two players is a single, powerful query.

    ```python
    # backend/db/graph_crud.py
    def find_shortest_path_between_players(player1_id: int, player2_id: int):
        query = """
        MATCH path = shortestPath(
          (p1:Player {id: $p1_id})-[:TEAMMATE_IN*]-(p2:Player {id: $p2_id})
        )
        // Return a list of player names in the path
        RETURN [node in nodes(path) | node.fullName] as connection
        """
        results = graph_db.run_query(query, {"p1_id": player1_id, "p2_id": player2_id})
        return results[0]['connection'] if results else []
    ```

4.  **Update the API Endpoint:** Finally, update your `players.py` endpoint to use this new function.

    ```python
    # backend/api/endpoints/players.py
    # ... imports
    from backend.db import graph_crud
    from backend.db.graph_session import get_graph_db

    # ... (add get_graph_db to Depends)

    @router.get("/path/{player1_id}/{player2_id}")
    def get_path(player1_id: int, player2_id: int, db = Depends(get_graph_db)):
        path = graph_crud.find_shortest_path_between_players(player1_id, player2_id)
        if not path:
            raise HTTPException(status_code=404, detail="No connection found between players.")
        return {"path": path}
    ```

---

## Conclusion and Further Resources

Migrating to a graph database is more than a technical change; it's a shift in how you think about your data. By embracing the connected nature of your domain, you will simplify your backend logic, improve performance, and unlock a whole new world of features centered around player relationships.

**Helpful Resources:**

*   **Neo4j Website:** [https://neo4j.com/](https://neo4j.com/)
*   **Cypher Query Language Intro:** [https://neo4j.com/developer/cypher/](https://neo4j.com/developer/cypher/)
*   **Neo4j Python Driver Docs:** [https://neo4j.com/docs/python-manual/current/](https://neo4j.com/docs/python-manual/current/)
*   **Awesome-Neo4j (Community Resources):** [https://github.com/neo4j-contrib/awesome-neo4j](https://github.com/neo4j-contrib/awesome-neo4j)

This plan provides a clear path forward. Take it one step at a time, and you will build a more powerful and elegant backend for your application.
