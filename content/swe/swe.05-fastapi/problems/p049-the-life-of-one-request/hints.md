## Hint 1

Draw the onion of section 13.1: the middleware is the outer layer; inside it, FastAPI solves the dependencies, then calls the endpoint. On the way in, the order is clear. The tricky part is the way **out**. Ask: what does `await call_next(request)` wait for? The full response, or only the moment the response **starts** (status and headers known)?

## Hint 2

Three facts for this FastAPI version:
- `call_next` returns as soon as the inner app has **started** the response. The body is sent, and only then the background tasks run, **after** the middleware has returned the response object.
- Background tasks run after the response body is sent.
- The code after `yield` in a dependency (default scope) runs when FastAPI has completely finished the response: **after** the background tasks.

For `/fail`: the `HTTPException` is thrown into the generator at the `yield` (section 9.5), so the `except` branch runs, then `finally`, and only then is the exception turned into the 404 response that the middleware sees. The response built from an exception carries **no** background tasks.

## Hint 3

```text
/ok:   middleware before, dependency open, endpoint,
       middleware after (200)            <- response started
       background task                   <- after the body is sent
       dependency commit, dependency close
/fail: middleware before, dependency open, endpoint,
       dependency rollback, dependency close   <- exception thrown in at the yield
       middleware after (404)                  <- the error response; no background line
```
