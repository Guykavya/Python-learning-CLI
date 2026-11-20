# A WebSocket echo

Chapter sections 15.1 and 15.2. Write a WebSocket endpoint `/ws/echo` in `solution.py` (the app is `app`):

1. Accept the connection.
2. In a loop, receive a text message and send it back **upper-cased** (`"hello"` → `"HELLO"`).
3. If the message is `bye` (ignore upper/lower case and spaces around it, so `"  BYE "` counts too; `"bye now"` does not), send `"goodbye"` and then **close** the connection with code **1000** (normal closure), and stop.
4. If the client goes away first, `receive_text()` raises `WebSocketDisconnect`. Catch it so the endpoint ends quietly.

## Example

```text
client sends "hello"     -> server sends "HELLO"
client sends "bye now"   -> server sends "BYE NOW"
client sends "  BYE "    -> server sends "goodbye", then closes with code 1000
```

How a test reads the close (this is what the tests do):

```python
with client.websocket_connect("/ws/echo") as ws:
    ws.send_text("bye")
    print(ws.receive_text())   # goodbye
    print(ws.receive())        # {'type': 'websocket.close', 'code': 1000, 'reason': ''}
```

**Close codes** are numbers in the WebSocket protocol, like HTTP status codes: 1000 means "normal closure, all done"; you will meet 1008 (policy violation) and 1009 (message too big) in problem 41.
