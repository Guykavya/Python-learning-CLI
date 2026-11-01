- Creating the semaphore inside `status_of`. Every request then gets its own private
  semaphore, and nothing is limited.
- Awaiting each request in a `for` loop. That is a limit of 1, whatever `limit` says.
- Taking the semaphore only around building the request, then sending it outside the
  `async with`. The slot must be held while the request is in flight.
- Calling `raise_for_status()`. Here 404 is the answer the link checker wants to report, not a
  crash that throws away every other result.
- Using `threading.Semaphore` in async code. Its `acquire()` blocks the whole event loop
  thread instead of letting other tasks run.
- Building the dict from the order of completion (appending as each finishes). `gather` already
  gives you input order; `zip` with `urls`.
