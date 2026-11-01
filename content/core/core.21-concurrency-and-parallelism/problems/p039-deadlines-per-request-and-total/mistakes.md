- Using only `per_request`. Each request is then capped, but nothing caps the batch: if the
  requests queue up anywhere (a concurrency limit, a busy server) 50 requests of 0.9 s each
  never time out yet can take 45 s together. The batch needs its own deadline.
- Using only `total`. One slow service then eats the whole budget, and you cannot tell "this
  request was slow" from "the batch ran out of time".
- Collecting results only after everything finished (`results = await gather(...)`). When the
  total deadline fires, `gather` is cancelled and every finished result is lost.
- `asyncio.wait(..., timeout=total)` without cancelling `pending`. The requests keep running
  after the function returned.
- Cancelling the pending tasks but not awaiting them. Their `finally` blocks (closing the
  response, here the fake server's bookkeeping) have not run yet when you return.
- `except Exception:` inside `fetch_one` to "catch the timeout". It also hides real errors, and
  in older Pythons `asyncio.TimeoutError` was a different class from `TimeoutError` (since 3.11
  they are the same).
- Catching `asyncio.CancelledError` in `fetch_one` and returning `"timeout"`. Swallowing the
  cancellation breaks the outer deadline: the TaskGroup thinks the task finished normally.
