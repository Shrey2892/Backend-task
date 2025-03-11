from fastapi import FastAPI, WebSocket
import uvicorn

app = FastAPI()
active_connections = []

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    
    try:
        while True:
            data = await websocket.receive_text()
            for conn in active_connections:
                await conn.send_text(f"Message: {data}")
    except:
        pass
    finally:
        active_connections.remove(websocket)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
