- Appending to `results` inside the `as_completed` loop. That builds the list in completion
  order; the caller then matches result `i` with the wrong job.
- Looping `for fut in futures: fut.result()` in submission order. Results are right, but
  progress for a fast job waits behind a slow one.
- Calling `f()` inside `submit(f())`. That runs the job right now in your thread and submits
  its *result*. Pass the function: `submit(f)`.
- Using `add_done_callback(lambda fut: on_done(...))`. The callback runs in a worker thread,
  so several callbacks can run at the same time and a progress bar needs a lock.
- Keeping a counter `done_count` and passing it as the index. The index must identify the
  job, not say how many jobs have finished.
- Forgetting `max_workers=workers`. The default (`min(32, cpu_count + 4)`) silently ignores
  the caller's limit.
