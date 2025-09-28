from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json
from backend.game.guess_game import GuessGame


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
    
    game = GuessGame()
    await game.start_new_game(1, 2)
    await manager.broadcast(json.dumps({
        "message": f"The game is starting...",
        "current_player": str(game.current_player.id)
    }))

    try:
        while True:
            data_str = await websocket.receive_text()
            print(f"Received data: {data_str}")
            data = json.loads(data_str)
            print(f"Parsed data: {data}")
            # Here, you would process the incoming data
            # e.g., data = {"action": "guess", "payload": 8474660}
            # 1. Pass to your game logic module
            game_state = await game.make_guess(game.get_current_player_turn(), data['payload'])
            # 2. Get updated game state
            # 3. Broadcast the new state to all players
            await manager.broadcast(json.dumps(game_state))
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(json.dumps({"message": "A player has left the battle."}))