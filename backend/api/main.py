from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from backend.db import session, models
from backend.api.endpoints import players, battle

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
app.include_router(battle.router, tags=["battle"])
