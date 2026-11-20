# Request id and timing middleware

Chapter section 13.1. When something goes wrong in production, the first question is "which request was it?". A **request id** is a short string that travels with one request: the client (or a proxy in front of you) may send one in the `X-Request-ID` header, your logs print it, and the response carries it back so the user can quote it in a bug report. Next to it, a **timing header** tells you how long the server worked on the request.

Neither belongs to one endpoint, so they belong in **middleware**. In `solution.py` add one `@app.middleware("http")` function to the given app that does the following for **every** response, including 404s for unknown paths:

1. **Request id.** Read the incoming `X-Request-ID` header. Reuse it **only if it is valid**: 1 to 64 characters, each one a letter, a digit, `-` or `_` (use the given `VALID_ID = re.compile(r"[A-Za-z0-9_-]{1,64}")` with `fullmatch`). Otherwise (missing, too long, spaces, `<script>`...) create a new one with `uuid.uuid4().hex` (32 hexadecimal characters).
   Store it in `request.state.request_id` **before** calling `call_next`, so endpoints can read it, and put it in the response header `X-Request-ID`.
2. **Timing.** Measure with `time.perf_counter()` around `call_next` and add the header `Server-Timing: app;dur=<milliseconds>` with the milliseconds written with **one decimal** (for example `app;dur=0.4`). `Server-Timing` is a standard header that browser developer tools display.

The endpoint `GET /ping` is already written: it returns `{"request_id": request.state.request_id}`.

## Example

```text
GET /ping   X-Request-ID: order-42
  -> 200 {"request_id": "order-42"}   X-Request-ID: order-42   Server-Timing: app;dur=0.6

GET /ping   (no header)
  -> 200 {"request_id": "9f1c...(32 hex)"}   X-Request-ID: the same 32 hex characters

GET /ping   X-Request-ID: <script>
  -> a fresh 32-hex id (the bad one is NOT echoed back)

GET /nowhere
  -> 404, and still X-Request-ID and Server-Timing
```

(The duration is machine-specific; the tests check only its format.)

## Why refuse a bad incoming id?

The id ends up in your logs and in the response. A client could send a huge value, or one with HTML or control characters, to fill your logs or to confuse a log viewer. Accepting only a short, plain id costs one regular expression.
