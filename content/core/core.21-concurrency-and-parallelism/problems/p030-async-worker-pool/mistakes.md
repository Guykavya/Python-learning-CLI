- Calling `task_done()` only after a successful `worker(item)`. One failure and
  `queue.join()` hangs forever.
- Letting the worker's exception escape the loop. That worker dies; with few workers, the
  rest of the queue may never be processed and `join()` hangs.
- Returning after `join()` without cancelling the workers. They stay paused in `get()`;
  `asyncio.run` cancels them at the very end, but in a long-running program they leak.
- Cancelling the workers but not awaiting them. `cancel()` only requests; the tasks have not
  ended yet when you return.
- Appending results as they finish. The order is then finishing order, not input order.
- Creating one task per item "plus" a queue. The point of a pool is that only `n_workers`
  tasks exist.
