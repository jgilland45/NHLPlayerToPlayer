from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.core.config import settings

# Create the SQLAlchemy engine using the database URL from settings
engine = create_engine(
    settings.DATABASE_URL,
    # This argument is needed for SQLite to allow multithreading
    connect_args={"check_same_thread": False}
)

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
