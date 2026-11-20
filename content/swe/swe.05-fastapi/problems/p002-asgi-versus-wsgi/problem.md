# ASGI versus WSGI

Chapter section 1.1 (and the layer diagram in 1.2). Your Flask app from swe.04 runs under Gunicorn with **one sync worker**. Two requests arrive at the same moment. The first one calls a slow outside API that takes **2 seconds** to answer; the second one only reads a small value and would take 5 milliseconds.

In `answer.md` write a clear explanation (about 150 to 250 words) that answers:

1. **What happens to the second request** under that one WSGI worker, and why? Use the WSGI call `app(environ, start_response)` in your answer.
2. **What does an event loop add?** Explain what `await` lets the loop do while the first request is waiting, and why one thread can then serve both requests.
3. **Why do WebSockets need ASGI?** Say what a WebSocket connection does over time, and which part of the ASGI signature `app(scope, receive, send)` makes it possible.
4. One honest limit: what does `async` **not** speed up? (Think of a loop that computes something for 2 seconds with no waiting.)

A good answer uses the words *worker*, *blocking*, *event loop*, *await*, *connection*, *message*.

## Example

A sentence in the expected style: "Under WSGI the worker is stuck inside `app(environ, start_response)` until the response is finished, so ..."
