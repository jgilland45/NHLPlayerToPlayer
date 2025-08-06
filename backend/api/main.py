from fastapi import FastAPI
from contextlib import asynccontextmanager
from backend.db import session
from backend.api.endpoints import players, battle

# run using `uvicorn backend.api.main:app --reload`

@asynccontextmanager
async def lifespan(app: FastAPI):
    # The graph_db driver is initialized on import and is meant to be long-lived.
    # This context manager ensures its `close()` method is called gracefully on shutdown.
    yield
    # Clean up the resources
    session.get_graph_db().close()

app = FastAPI(title="NHL Player-to-Player API", lifespan=lifespan)

@app.get("/")
async def read_root():
    return {"message": "Welcome to the NHL Player-to-Player API"}

# Include routers from other files
app.include_router(players.router, prefix="/players", tags=["players"])
app.include_router(battle.router, tags=["battle"])
