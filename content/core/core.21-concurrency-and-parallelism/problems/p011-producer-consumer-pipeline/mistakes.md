- Putting only **one** sentinel. One worker stops; the others wait in `get()` forever and
  `join()` never returns.
- Stopping when `jobs.empty()` is true. A worker can see an empty queue before the producer
  has put anything, and quit too early. `empty()` is only a snapshot.
- Testing `if not job:` for the sentinel. The item `0` or `""` looks like a stop signal.
- Putting the sentinels **before** the real items, or from a worker thread. Workers then stop
  before the work is done.
- Using a plain list with `pop()` as the queue. Two workers can take the same item or crash on
  an empty list; `queue.Queue` does the locking and the waiting for you.
- Forgetting to `join()` the workers, so `pipeline` returns while results are still being
  written.
