import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import Dict

app = FastAPI()

# Dictionary to track connected WebSocket clients
active_connections: Dict[str, WebSocket] = {}

@app.websocket("/ws/chat/{room_name}/{username}")
async def websocket_endpoint(websocket: WebSocket, room_name: str, username: str):
    await websocket.accept()
    active_connections[f"{room_name}:{username}"] = websocket

    try:
        while True:
            data = await websocket.receive_text()
            # Broadcast the message to all users in the same room
            for key, connection in active_connections.items():
                if key.startswith(room_name):
                    await connection.send_text(f"{username}: {data}")

    except WebSocketDisconnect:
        del active_connections[f"{room_name}:{username}"]

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
