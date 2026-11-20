## Model answer

**1. One WSGI worker.** WSGI is a synchronous, one-shot contract: the server calls `app(environ, start_response)` and gets the whole response back when the function returns. While the first request's handler waits 2 seconds for the outside API, the worker's thread is **blocked** inside that call and does nothing else. The second request waits in the queue for about 2 seconds, although its own work takes 5 ms. To serve more slow requests at once, WSGI needs more threads or processes.

**2. The event loop.** Under ASGI the app is `async def app(scope, receive, send)` and every slow step is `await`ed. An `await` on network I/O hands control back to the **event loop**, which runs another task that is ready. So while request 1 waits for the API, the loop runs request 2 to the end, then comes back to request 1 when its answer arrives. One thread keeps many requests "in flight"; none of them sits idle holding the thread.

**3. WebSockets.** A WebSocket is a long-lived **connection** that carries many **messages** in both directions, for minutes. A WSGI call returns one finished response, so it has no way to say "send this now, and another message later". In ASGI, `receive` and `send` are async functions you can call many times during one call of the app, so one call = one connection with many messages.

**4. The limit.** `async` helps only when tasks *wait*. A CPU-bound loop of 2 seconds never reaches an `await`, so it blocks the event loop and every other request; such work belongs in a thread, a process or a task queue.

**Checklist: your answer should mention**
- [ ] WSGI calls `app(environ, start_response)` once and gets a whole response: synchronous and one-shot
- [ ] the worker thread is blocked during the 2 s wait, so the second request waits too
- [ ] WSGI scales slow requests only with more threads or processes
- [ ] `await` gives control back to the event loop, which runs another ready request meanwhile
- [ ] one thread can keep many requests in flight because most of their time is waiting
- [ ] a WebSocket is one long connection with many messages; `receive`/`send` can be called many times in one ASGI call
- [ ] async does not speed up CPU-bound work; it blocks the loop
