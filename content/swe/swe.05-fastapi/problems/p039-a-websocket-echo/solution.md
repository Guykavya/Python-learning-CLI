## Approach

```python
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
```

Example: the client sends `"  Bye  "`. `strip()` gives `"Bye"`, `lower()` gives `"bye"`, so the server sends `"goodbye"` and a close frame with code 1000. The test then sends one more message; a correct server has already closed, so the test receives the close message `{'type': 'websocket.close', 'code': 1000, ...}` instead of an answer.

Two ways a WebSocket ends: the **server** closes (here, after `bye`), or the **client** leaves (closing the tab, losing the network). The second shows up on the server as `WebSocketDisconnect` raised by `receive_text()`; without the `except` it would be an error in the server log each time someone closes a tab.

## Complexity

O(n) per message of n characters (`upper()`); the connection itself holds a little memory for as long as it is open.

## Another way

Use `async for text in websocket.iter_text():` instead of `while True` + `receive_text()`. The loop ends by itself when the client disconnects, so no `except WebSocketDisconnect` is needed; you still `close(code=1000)` and `return` (or `break`) for `bye`.
