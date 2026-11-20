from fastapi import FastAPI, WebSocket, WebSocketDisconnect

TOKENS = {"t-asha": "asha", "t-ben": "ben"}
MAX_BYTES = 4096


def user_from_token(token):
    """The user name for a token, or None. (A real app would decode a JWT here.)"""
    return TOKENS.get(token)


app = FastAPI()


@app.websocket("/ws/chat")
async def chat(websocket: WebSocket, token: str = ""):
    # TODO: refuse a bad token with close(code=1008) BEFORE accept()
    # TODO: close with code 1009 when a message is over MAX_BYTES bytes (UTF-8)
    user = user_from_token(token) or "anonymous"
    await websocket.accept()
    try:
        while True:
            text = await websocket.receive_text()
            await websocket.send_text(f"{user}: {text}")
    except WebSocketDisconnect:
        pass
