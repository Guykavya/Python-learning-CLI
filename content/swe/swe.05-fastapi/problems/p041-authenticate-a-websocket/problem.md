# Authenticate a WebSocket

Chapter section 15.4 (and 15.2). A browser cannot add an `Authorization` header to `new WebSocket(...)`, so the token travels in the **query string**: `/ws/chat?token=...`. And because the connection stays open for a long time, the server must protect itself against huge messages.

`solution.py` gives you `TOKENS`, a dict from token to user name (in a real app this would be a JWT check as in section 12), and the helper `user_from_token(token)` that returns the user name or `None`. Write the WebSocket endpoint `/ws/chat` with a query parameter `token: str = ""`:

1. **Check the token before accepting.** If `user_from_token(token)` is `None` (wrong, empty or missing token), call `await websocket.close(code=1008)` **without** calling `accept()`, and return. 1008 means "policy violation". The client never gets a working connection.
2. Otherwise `accept()` and loop: receive a text message and send back `"<user>: <text>"`.
3. **Size limit.** If a message is longer than `MAX_BYTES = 4096` **bytes** when encoded as UTF-8, close with code **1009** ("message too big") and return. Exactly 4096 bytes is still allowed. Count bytes, not characters: `"é"` is 1 character but 2 bytes.
4. Catch `WebSocketDisconnect` so a client leaving is quiet.

## Example

```text
/ws/chat?token=t-asha   send "hi"           -> "asha: hi"
/ws/chat?token=nope     -> refused during the handshake, close code 1008
/ws/chat                -> refused, close code 1008
/ws/chat?token=t-ben    send "x" * 4096      -> "ben: xxxx..."
                        send "x" * 4097      -> connection closed with code 1009
```

How the tests see a refused handshake:

```python
from starlette.websockets import WebSocketDisconnect

with pytest.raises(WebSocketDisconnect) as info:
    with client.websocket_connect("/ws/chat?token=nope"):
        pass
assert info.value.code == 1008
```

If your endpoint accepted first and closed afterwards, `websocket_connect` would succeed and no exception would be raised: the test can tell the difference.
