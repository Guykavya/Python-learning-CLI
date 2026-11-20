from fastapi import FastAPI, WebSocket, WebSocketDisconnect


class ConnectionManager:
    def __init__(self):
        self.rooms = {}                      # room name -> list of WebSocket

    async def connect(self, room, websocket):
        await websocket.accept()
        self.rooms.setdefault(room, []).append(websocket)

    def disconnect(self, room, websocket):
        sockets = self.rooms.get(room, [])
        if websocket in sockets:
            sockets.remove(websocket)
        if not sockets:
            self.rooms.pop(room, None)       # do not leak empty rooms

    async def broadcast(self, room, message):
        for connection in list(self.rooms.get(room, [])):     # a copy: disconnect() may change the list
            try:
                await connection.send_json(message)
            except Exception:
                self.disconnect(room, connection)              # dead socket: drop it, keep going

    def count(self, room):
        return len(self.rooms.get(room, []))                   # .get: never creates a room


manager = ConnectionManager()
app = FastAPI()


@app.websocket("/ws/rooms/{room}")
async def room_socket(websocket: WebSocket, room: str, user: str):
    await manager.connect(room, websocket)
    await manager.broadcast(room, {"event": "joined", "user": user})
    try:
        while True:
            data = await websocket.receive_json()
            await manager.broadcast(room, {"event": "message", "user": user, "data": data})
    except WebSocketDisconnect:
        manager.disconnect(room, websocket)
        await manager.broadcast(room, {"event": "left", "user": user})


@app.post("/rooms/{room}/announce")
async def announce(room: str, text: str):
    await manager.broadcast(room, {"event": "announcement", "text": text})
    return {"delivered_to": manager.count(room)}
