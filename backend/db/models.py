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
