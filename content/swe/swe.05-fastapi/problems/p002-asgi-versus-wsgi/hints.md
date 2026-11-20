## Hint 1

What is the worker thread **doing** during the 2 seconds? Is it computing, or waiting? Can a plain function call `app(environ, start_response)` stop halfway and let someone else use the thread?

## Hint 2

Compare the two signatures in section 1.1. In ASGI, what can happen at every `await`? How many times may `send` be called during one call of the app, and why does that matter for a chat connection that stays open for ten minutes?

## Hint 3

```text
1. WSGI: one call -> one finished response; thread blocked while waiting; request 2 waits ~2 s
2. ASGI: await on I/O -> loop runs request 2 -> back to request 1 when the API answers
3. WebSocket: one connection, many messages; receive/send called many times in one app call
4. limit: CPU work never awaits -> blocks the loop
```
