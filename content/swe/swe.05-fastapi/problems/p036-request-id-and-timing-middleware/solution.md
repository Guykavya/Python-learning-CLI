## Approach

The work splits around `call_next`. Before it: decide the id and store it where the endpoint can see it, and start the clock. After it: stop the clock and decorate the response.

```python
@app.middleware("http")
async def request_id_and_timing(request: Request, call_next):
    incoming = request.headers.get("x-request-id", "")
    request_id = incoming if VALID_ID.fullmatch(incoming) else uuid.uuid4().hex
    request.state.request_id = request_id          # before call_next: endpoints can read it
    start = time.perf_counter()
    response = await call_next(request)            # the router, the endpoint (or the 404) run here
    elapsed_ms = (time.perf_counter() - start) * 1000
    response.headers["X-Request-ID"] = request_id
    response.headers["Server-Timing"] = f"app;dur={elapsed_ms:.1f}"
    return response
```

Example: `GET /nowhere` with `X-Request-ID: lost-1`. The middleware accepts `lost-1`, calls `call_next`, the router finds no route and produces a 404 response, and that 404 comes back through the middleware, which adds both headers. This is why middleware, not a dependency, is the right tool: a dependency runs only when a route matched.

`request.headers` is case-insensitive, so `"x-request-id"` finds `X-Request-ID`. `time.perf_counter()` is the right clock for durations (it never jumps when the system clock is adjusted).

## Complexity

O(L) for the regular expression on an id of length L (at most 64 characters are accepted); the timing is two clock reads. Middleware runs on every request, so it must stay this cheap.

## Another way

Write it as a class (pure ASGI middleware, the form of section 1.2) and add it with `app.add_middleware(...)`; that form can also see WebSocket connections and avoids some overhead of `@app.middleware("http")`. Libraries such as `asgi-correlation-id` do exactly this and also put the id into every log line through a `logging.Filter`.
