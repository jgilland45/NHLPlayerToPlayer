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
