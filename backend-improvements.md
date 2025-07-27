
# Backend Code Review & Improvement Roadmap

This document provides a detailed, professional-grade code review of your backend systems and a strategic roadmap for improvement. The feedback is direct and opinionated, designed to give you a clear path toward a robust, scalable, and production-ready application.

---

## High-Level Architecture Assessment

**Compliment:** You've successfully built functional components for your application's core needs: a data pipeline to get NHL data, a REST API to serve it, and a real-time server for multiplayer concepts. This is a huge accomplishment. You have working prototypes of all the hard parts.

**Critique:** The biggest issue is **fragmentation and inconsistency**. The backend is spread across two languages (Python, Node.js), multiple frameworks (FastAPI, Express, Socket.IO), and several disconnected scripts. This creates significant challenges:

*   **High Cognitive Load:** Anyone (including you) working on the project needs to be an expert in multiple tech stacks.
*   **Maintenance Nightmare:** A bug in data handling might require touching a Python script, a Node.js API, and the database schema. This is slow and error-prone.
*   **No Single Source of Truth:** There are multiple database schemas defined (one implicitly in `webscrapetest.py`, one in `create_tables.py`), multiple API servers, and duplicated logic.
*   **Scalability Issues:** The current real-time server stores state in-memory, making it impossible to scale beyond a single instance. The database is accessed via raw, manually locked cursors, which is inefficient and dangerous.

**Core Recommendation:** **Unify the entire backend into a single, modern Python application.**

Your data pipeline is already in Python, and FastAPI is an excellent, high-performance choice that also has first-class support for WebSockets. This consolidation will dramatically simplify development, deployment, and maintenance.

---

## Part 1: The Great Unification (Action Plan)

Let's start by cleaning up the project structure.

**1. Reorganize the Directory Structure:**

I will perform these actions for you, but here is the plan:

```bash
# 1. Create a new, clean backend directory
mkdir -p backend_new/api backend_new/core backend_new/db backend_new/data_pipeline

# 2. Move the relevant Python code into the new structure
mv database_test/api_server.py backend_new/api/main.py
mv database_test/db_getters.py backend_new/db/getters.py
mv database_test/db_inserts.py backend_new/db/inserts.py
mv database_test/create_tables.py backend_new/db/manage_schema.py
mv database_test/data_pipeline.py backend_new/data_pipeline/run_pipeline.py

# 3. Create placeholder files for our new structure
touch backend_new/core/config.py
touch backend_new/db/models.py
touch backend_new/db/session.py
touch backend_new/requirements.txt

# 4. Get rid of the old, fragmented directories
rm -rf backend/
rm -rf database_test/

# 5. Rename the new backend to be the official one
mv backend_new backend
```

**2. Adopt a Professional Python Backend Structure:**

Your new `backend` directory should look like this:

```
backend/
├── data_pipeline/
│   ├── __init__.py
│   ├── run_pipeline.py   # Main script to orchestrate data collection
│   └── sources.py        # Functions for hitting NHL APIs
├── api/
│   ├── __init__.py
│   ├── main.py           # Main FastAPI app entrypoint
│   └── endpoints/
│       ├── __init__.py
│       ├── players.py    # Router for player-related endpoints
│       └── games.py      # Router for game-related endpoints
├── db/
│   ├── __init__.py
│   ├── models.py         # SQLAlchemy ORM models (the schema)
│   ├── session.py        # Database session management
│   └── crud.py           # Replaces getters.py and inserts.py (Create, Read, Update, Delete)
├── core/
│   ├── __init__.py
│   └── config.py         # Configuration management (env vars)
├── tests/
│   ├── __init__.py
│   └── test_players_api.py
├── Dockerfile
├── requirements.txt
└── README.md
```

This structure separates concerns, making the code clean, testable, and easy to navigate.

---

## Part 2: Refactoring the Data Pipeline

**Critique:** Your current data scripts (`addPlayerIDToDB.py`, `webscrapetest.py`, `data_pipeline.py`) are a mix of scraping, data transformation, and direct database inserts. They use brittle `time.sleep()` calls, have minimal error handling, and are not idempotent (re-running them could cause errors or duplicates).

**Recommendation:** Rebuild this as a modern, robust ETL (Extract, Transform, Load) process.

### Step 1: Extract - Robust API Interaction

Create `backend/data_pipeline/sources.py`. This file should *only* be responsible for fetching data from the NHL API.

```python
# backend/data_pipeline/sources.py
import httpx
import asyncio
import logging
from typing import List, Dict, Any

# Use a logger for better debugging
logger = logging.getLogger(__name__)

# Base URL for the new NHL API
NHL_API_BASE_URL = "https://api-web.nhle.com/v1"

async def fetch_game_boxscore(client: httpx.AsyncClient, game_id: int) -> Dict[str, Any]:
    """Fetches the boxscore for a single game."""
    url = f"{NHL_API_BASE_URL}/gamecenter/{game_id}/boxscore"
    try:
        response = await client.get(url, timeout=10.0)
        response.raise_for_status()  # Raises an exception for 4xx/5xx status codes
        return response.json()
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error fetching game {game_id}: {e.response.status_code} - {e.response.text}")
    except httpx.RequestError as e:
        logger.error(f"Request error for game {game_id}: {e}")
    return {}

async def get_all_game_ids_for_season(season: int = 2023) -> List[int]:
    """Gets all game IDs for a given season."""
    # This endpoint needs to be found or built, assuming one exists.
    # For now, let's assume a placeholder.
    # In a real scenario, you might need to iterate through schedules.
    # Example: 'https://api.nhle.com/stats/rest/en/game?season=20232024'
    # The logic from your old scripts can be adapted here.
    logger.info(f"Fetching all game IDs for {season}-{season+1} season.")
    # This is a simplified placeholder.
    # You would adapt your existing logic for getting all games here.
    return list(range(2023020001, 2023021312 + 1)) # Example range for a full season
```

**Key Improvements:**
*   **`httpx` with `AsyncClient`:** Allows for making requests asynchronously, which is much faster than making them one by one.
*   **`response.raise_for_status()`:** Proper, immediate error handling for bad HTTP responses.
*   **Logging:** Provides clear insight into what the script is doing and where it fails.
*   **No `time.sleep()`:** We'll handle rate limiting gracefully at the execution level.

### Step 2: Transform & Load - Using an ORM

An Object-Relational Mapper (ORM) like SQLAlchemy is the industry standard for interacting with databases in Python. It prevents SQL injection, manages database connections for you, and makes your code far more readable and maintainable.

First, define your database schema in `backend/db/models.py`.

```python
# backend/db/models.py
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class Player(Base):
    __tablename__ = 'players'
    id = Column(Integer, primary_key=True)
    full_name = Column(String, nullable=False)

class Team(Base):
    __tablename__ = 'teams'
    # A team in a given season, e.g., 'BOS2023'
    id = Column(String, primary_key=True)
    tricode = Column(String, nullable=False)
    season = Column(Integer, nullable=False)

class Game(Base):
    __tablename__ = 'games'
    id = Column(Integer, primary_key=True)
    season = Column(Integer, nullable=False)

# This is a "many-to-many" association table
class PlayerGameStats(Base):
    __tablename__ = 'player_game_stats'
    player_id = Column(Integer, ForeignKey('players.id'), primary_key=True)
    game_id = Column(Integer, ForeignKey('games.id'), primary_key=True)
    team_id = Column(String, ForeignKey('teams.id'), nullable=False)
    
    # Relationships (optional but useful)
    player = relationship("Player")
    game = relationship("Game")
    team = relationship("Team")
```

Now, create a `crud.py` file to handle database operations. This replaces all your `db_getters.py` and `db_inserts.py` files.

```python
# backend/db/crud.py
from sqlalchemy.orm import Session
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from . import models
from typing import List, Dict, Any

def bulk_insert_players_from_game_data(db: Session, game_data: Dict[str, Any]):
    """
    Extracts player info from a game's boxscore and inserts them
    into the database if they don't already exist.
    """
    players_to_insert = []
    
    def extract_players(team_roster: Dict[str, Any]):
        for position in ['forwards', 'defense', 'goalies']:
            for player in team_roster.get(position, []):
                players_to_insert.append({
                    "id": player['playerId'],
                    "full_name": f"{player['firstName']['default']} {player['lastName']['default']}"
                })

    extract_players(game_data['playerByGameStats']['homeTeam'])
    extract_players(game_data['playerByGameStats']['awayTeam'])

    if not players_to_insert:
        return

    # "INSERT OR IGNORE" for SQLite
    stmt = sqlite_insert(models.Player).values(players_to_insert)
    stmt = stmt.on_conflict_do_nothing(index_elements=['id'])
    db.execute(stmt)
    db.commit()
```

**Key Improvements:**
*   **Single Source of Truth:** The `models.py` file is now the canonical definition of your database schema.
*   **Idempotency:** Using `on_conflict_do_nothing` (the equivalent of `INSERT OR IGNORE`) makes your data loading safe to re-run.
*   **Readability:** The code is declarative. You define *what* your data looks like, and SQLAlchemy handles the SQL.
*   **Security:** The ORM handles parameterization, protecting you from SQL injection vulnerabilities.

---

## Part 3: Refactoring the API Server

**Critique:** Your FastAPI server (`api_server.py`) is a good starting point but will become a single massive file that's hard to manage. The database access is not safe for a web server. The Node.js server (`app.js`, `dbAPI.js`) is now redundant.

**Recommendation:** Structure your FastAPI application for growth and implement safe, efficient database handling.

### Step 1: Application and Database Session Setup

FastAPI's dependency injection system is perfect for managing database connections.

```python
# backend/db/session.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# In a real app, this comes from config.py
DATABASE_URL = "sqlite:///./nhl_app.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# backend/api/main.py
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from ..db import session, models
from .endpoints import players, games

# Create all tables defined in models.py
models.Base.metadata.create_all(bind=session.engine)

app = FastAPI(title="NHL Player-to-Player API")

# Dependency to get a DB session
def get_db():
    db = session.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "Welcome to the NHL Player-to-Player API"}

# Include routers from other files
app.include_router(players.router, prefix="/players", tags=["players"])
app.include_router(games.router, prefix="/games", tags=["games"])

```

### Step 2: Create API Routers

Break your endpoints into logical groups.

```python
# backend/api/endpoints/players.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ...db import crud, models
from ... import schemas # We'll create this file for Pydantic models
from ..main import get_db

router = APIRouter()

@router.get("/{player_id}", response_model=schemas.Player)
def get_player_by_id(player_id: int, db: Session = Depends(get_db)):
    player = crud.get_player(db, player_id=player_id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    return player

@router.get("/{player_id}/teammates", response_model=List[schemas.Player])
def get_player_teammates(player_id: int, db: Session = Depends(get_db)):
    teammates = crud.get_teammates_for_player(db, player_id=player_id)
    return teammates
```

You'll also need `schemas.py` to define the shape of your API data using Pydantic.

```python
# backend/schemas.py
from pydantic import BaseModel
from typing import List

class PlayerBase(BaseModel):
    id: int
    full_name: str

class Player(PlayerBase):
    class Config:
        orm_mode = True # Allows Pydantic to read data from ORM models
```

**Key Improvements:**
*   **Dependency Injection (`Depends(get_db)`):** This is the biggest win. FastAPI now manages the lifecycle of your database sessions. It's safe, efficient, and clean. No more global cursors or manual locks.
*   **`APIRouter`:** Your API can now be split across multiple files, keeping your project organized as it grows.
*   **Pydantic Schemas:** Your API now has automatic request validation and response serialization. It also generates OpenAPI documentation for free.
*   **Clear Separation:** The API endpoint is only responsible for handling the HTTP request/response. The actual database logic lives in `crud.py`.

---

## Part 4: Architecting Real-Time Multiplayer

**Critique:** The `app.js` Socket.IO server is a great proof-of-concept but has two critical flaws for production:
1.  **In-Memory State:** The `backendPlayers` object will be lost on restart and, more importantly, will not be shared if you run more than one server process.
2.  **Node.js:** It requires you to maintain and deploy a completely separate technology stack.

**Recommendation:** Use FastAPI's built-in WebSocket support and a Redis backend for state management. This keeps your stack unified and makes it scalable.

### The Architecture

1.  **Client:** Connects to a WebSocket endpoint like `ws://your-api.com/ws/game/{game_id}`.
2.  **FastAPI WebSocket Endpoint:** Manages the connection. It receives messages from the client and passes them to the appropriate "game room". It listens for updates from the game room and broadcasts them to all connected clients.
3.  **Game Room Logic:** A Python class (`GameRoom`) that encapsulates the rules of your "battle" mode. It doesn't know about WebSockets, only about game state and rules.
4.  **Redis:** A very fast in-memory database. Used to store the state of all active games and to pass messages between your FastAPI server instances (if you scale up).

### Example Implementation

```python
# backend/api/endpoints/battle.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json

router = APIRouter()

class ConnectionManager:
    """Manages active WebSocket connections for a single game room."""
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

# This would be a dictionary of managers, one for each active game
# In a real app, this state should live in Redis, not in-memory.
game_managers = {}

@router.websocket("/ws/{game_id}")
async def websocket_endpoint(websocket: WebSocket, game_id: str):
    if game_id not in game_managers:
        game_managers[game_id] = ConnectionManager()
    
    manager = game_managers[game_id]
    await manager.connect(websocket)
    
    # Announce new player
    await manager.broadcast(json.dumps({"message": f"Player has joined the battle!"}))

    try:
        while True:
            data = await websocket.receive_text()
            # Here, you would process the incoming data
            # e.g., data = {"action": "GUESS_TEAMMATE", "payload": "Wayne Gretzky"}
            # 1. Pass to your game logic module
            # 2. Get updated game state
            # 3. Broadcast the new state to all players
            await manager.broadcast(f"A player sent: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(json.dumps({"message": "A player has left the battle."}))

```
*In `main.py`, you would add `app.include_router(battle.router, tags=["battle"])`.*

**This is a simplified example.** A production system would use Redis's Pub/Sub feature to broadcast messages instead of the in-memory `ConnectionManager`, which would allow you to run multiple, independent FastAPI server processes.

---

This roadmap is a significant undertaking, but it's a standard and proven path for taking a project from a collection of scripts to a professional, scalable application. By following it, you will not only get your app deployed but also gain invaluable experience in modern backend engineering practices.
