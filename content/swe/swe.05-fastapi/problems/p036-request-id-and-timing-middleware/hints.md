## Hint 1

Middleware has two halves: code **before** `await call_next(request)` (the request is on its way in) and code **after** it (the response is on its way out). Which of the two jobs belong before, which after? The endpoint must already see `request.state.request_id`, so where must that line go?

## Hint 2

Validate the incoming id with `VALID_ID.fullmatch(text)`. `fullmatch` (not `match` or `search`) makes sure the **whole** string fits the pattern. `request.headers.get("x-request-id", "")` gives an empty string when the header is missing, and an empty string does not match `{1,64}`, so one test covers both cases.

## Hint 3

```text
@app.middleware("http")
async def request_id_and_timing(request, call_next):
    incoming = header x-request-id or ""
    request_id = incoming if it fullmatches VALID_ID else uuid4().hex
    request.state.request_id = request_id
    start = perf_counter()
    response = await call_next(request)
    ms = (perf_counter() - start) * 1000
    response.headers["X-Request-ID"] = request_id
    response.headers["Server-Timing"] = f"app;dur={ms:.1f}"
    return response
```
