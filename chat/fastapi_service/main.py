from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import Dict, Set

app = FastAPI()

# Dictionary to track active connections { room_name: set(websockets) }
active_connections: Dict[str, Set[WebSocket]] = {}

@app.websocket("/ws/chat/{room_name}/{username}")
async def websocket_endpoint(websocket: WebSocket, room_name: str, username: str):
    await websocket.accept()

    # Add user to the room
    if room_name not in active_connections:
        active_connections[room_name] = set()
    
    active_connections[room_name].add(websocket)

    try:
        while True:
            data = await websocket.receive_text()
            message = f"{username}: {data}"

            # Broadcast message to all clients in the room
            for connection in active_connections[room_name].copy():
                try:
                    await connection.send_text(message)
                except:
                    active_connections[room_name].remove(connection)  # Remove disconnected client

    except WebSocketDisconnect:
        active_connections[room_name].remove(websocket)
        if not active_connections[room_name]:  # Cleanup empty rooms
            del active_connections[room_name]

