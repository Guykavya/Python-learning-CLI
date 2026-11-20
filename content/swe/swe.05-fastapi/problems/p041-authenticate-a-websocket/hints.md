## Hint 1

Two moments matter: **before** `accept()` (the handshake is still going on, you can refuse it) and **inside the loop** (every message). Which check belongs to which moment? What does the client see if you accept first and close a moment later?

## Hint 2

Refuse: `await websocket.close(code=1008)` and then `return`, with no `accept()` before it. Size: `len(text.encode("utf-8")) > MAX_BYTES` (strictly greater: 4096 is allowed). Then `await websocket.close(code=1009)` and `return`.

## Hint 3

```text
user = user_from_token(token)
if user is None: await close(code=1008); return
await accept()
try:
    loop:
        text = await receive_text()
        if len(text.encode("utf-8")) > MAX_BYTES: await close(code=1009); return
        await send_text(f"{user}: {text}")
except WebSocketDisconnect: pass
```
