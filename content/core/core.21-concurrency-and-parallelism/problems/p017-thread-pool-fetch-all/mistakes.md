- `executor.submit(fetch, url).result()` inside the submit loop. Each `result()` waits for that
  job before the next is submitted: sequential again.
- `executor.submit(fetch(url))`. That calls `fetch` right now, in the main thread. Pass the
  function and its argument separately.
- Not keeping a `future -> url` mapping, then guessing the URL from the position in
  `as_completed`. Completion order is not input order.
- Calling `future.result()` without `try`. The first failed URL raises out of `fetch_all` and
  the other results are lost.
- Forgetting `max_workers`. The default is `min(32, os.cpu_count() + 4)` threads, which may be
  more than the server allows.
- Storing `str(exc)` instead of the exception object.
