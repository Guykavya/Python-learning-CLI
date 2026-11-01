- Creating the semaphore **inside** `call`. Each thread gets its own semaphore with `limit`
  places, so nothing is limited.
- `threading.Semaphore()` without an argument. The default is 1 place, so everything runs one
  at a time.
- `sem.acquire()` and `sem.release()` without `try/finally`. A job that raises keeps its place
  forever, and with `limit=1` every later job waits forever.
- Using a `Lock` "because it is simpler". A lock is a semaphore with exactly one place; it
  cannot allow 3 at once.
- Collecting results with `append`, which gives finish order instead of input order.
