from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()


@app.websocket("/ws/echo")
async def echo(websocket: WebSocket):
    await websocket.accept()                          # finish the handshake
    try:
        while True:
            text = await websocket.receive_text()     # raises WebSocketDisconnect when the client leaves
            if text.strip().lower() == "bye":
                await websocket.send_text("goodbye")
                await websocket.close(code=1000)      # normal closure
                return                                # a closed socket cannot be read again
            await websocket.send_text(text.upper())
    except WebSocketDisconnect:
        pass                                          # the client left first: nothing to clean up
