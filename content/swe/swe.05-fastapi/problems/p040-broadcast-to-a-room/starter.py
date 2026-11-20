from fastapi import FastAPI, WebSocket, WebSocketDisconnect


class ConnectionManager:
    def __init__(self):
        self.rooms = {}                      # room name -> list of WebSocket

    async def connect(self, room, websocket):
        raise NotImplementedError("accept, then add the socket to the room")

    def disconnect(self, room, websocket):
        raise NotImplementedError("remove the socket; delete the room when it is empty")

    async def broadcast(self, room, message):
        raise NotImplementedError("send_json to every socket of the room; drop dead ones")

    def count(self, room):
        raise NotImplementedError("number of sockets in the room, 0 if unknown")


manager = ConnectionManager()
app = FastAPI()


@app.websocket("/ws/rooms/{room}")
async def room_socket(websocket: WebSocket, room: str, user: str):
    # TODO: connect, broadcast "joined", loop on receive_json -> broadcast "message",
    #       on WebSocketDisconnect: disconnect, broadcast "left"
    await websocket.close()


@app.post("/rooms/{room}/announce")
async def announce(room: str, text: str):
    # TODO: broadcast {"event": "announcement", "text": text}
    return {"delivered_to": 0}
