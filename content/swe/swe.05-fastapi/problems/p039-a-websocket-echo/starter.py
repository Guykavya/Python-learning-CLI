from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()


@app.websocket("/ws/echo")
async def echo(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            text = await websocket.receive_text()
            # TODO: "bye" (any case, spaces around) -> send "goodbye", close with code 1000, return
            # TODO: otherwise send the text upper-cased
            await websocket.send_text(f"echo: {text}")
    except WebSocketDisconnect:
        pass
