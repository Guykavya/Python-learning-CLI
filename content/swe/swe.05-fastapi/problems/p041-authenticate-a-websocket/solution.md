## Approach

```python
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
```

Example: `/ws/chat?token=nope`. `user_from_token("nope")` is `None`, so the server answers the handshake with a close (code 1008) instead of an accept. The test client's `websocket_connect` raises `WebSocketDisconnect(code=1008)` right away. A browser would see the `onclose` event with code 1008 and never an `onopen`.

Why check before `accept()`: an accepted socket is a working connection. Even for a moment it can receive broadcasts (in a room) and it holds resources. Refusing the handshake also tells the client clearly that the problem is authorisation, not the network.

Why count bytes: the cost to the server (memory, bandwidth) is in bytes. `"é" * 2049` passes a character check (2049 < 4096) but is 4098 bytes.

Note: the default token `""` makes a missing token reach your own check (1008). If you declare `token: str` without a default, FastAPI itself refuses a missing token with the same code 1008 (a validation error on a WebSocket closes it with 1008), so both work.

## Complexity

O(n) per message of n characters to encode it once for the size check.

## Another way

Real servers also limit the size at the protocol level: uvicorn's `--ws-max-size` (default 16 MiB) rejects bigger frames before your code ever sees them, which also protects against one giant frame filling memory. Your own check stays useful for an application limit smaller than the server's. And instead of a long-lived token in the URL (URLs end up in logs), give the browser a **short-lived ticket** from an authenticated HTTP endpoint and accept only that on the socket (section 15.4).
