## Hint 1

The chapter's echo endpoint (section 15.2) is almost the whole answer. What changes? The text you send back, and one special message that ends the loop. How do you compare `"  BYE "` with `"bye"` so that both count as the same word?

## Hint 2

`text.strip().lower() == "bye"` handles case and spaces. For the special case: `await websocket.send_text("goodbye")`, then `await websocket.close(code=1000)`, then `return` (after a close you must not call `receive_text` again). Keep the `try` / `except WebSocketDisconnect` around the whole loop.

## Hint 3

```text
accept
try:
    loop:
        text = await receive_text()
        if text.strip().lower() == "bye":
            await send_text("goodbye"); await close(code=1000); return
        await send_text(text.upper())
except WebSocketDisconnect: pass
```
