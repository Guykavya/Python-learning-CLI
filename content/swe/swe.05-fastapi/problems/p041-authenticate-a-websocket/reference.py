from fastapi import FastAPI, WebSocket, WebSocketDisconnect

TOKENS = {"t-asha": "asha", "t-ben": "ben"}
MAX_BYTES = 4096


def user_from_token(token):
    """The user name for a token, or None. (A real app would decode a JWT here.)"""
    return TOKENS.get(token)


app = FastAPI()


@app.websocket("/ws/chat")
async def chat(websocket: WebSocket, token: str = ""):
    user = user_from_token(token)
    if user is None:
        await websocket.close(code=1008)              # policy violation; never accepted
        return
    await websocket.accept()
    try:
        while True:
            text = await websocket.receive_text()
            if len(text.encode("utf-8")) > MAX_BYTES:
                await websocket.close(code=1009)      # message too big
                return
            await websocket.send_text(f"{user}: {text}")
    except WebSocketDisconnect:
        pass
