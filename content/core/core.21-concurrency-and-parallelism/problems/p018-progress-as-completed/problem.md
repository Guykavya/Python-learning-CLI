# Progress reports with `as_completed`

A command-line tool runs a batch of slow jobs (downloads, API calls) in a thread pool. The
user wants two things:

1. A progress line **the moment each job finishes**, so fast jobs are reported first.
2. At the end, the list of all results **in the order the jobs were given**, so the rest of
   the program can match result `i` with job `i`.

Write `run_with_progress(funcs, workers, on_done)` in `solution.py`:

- `funcs` is a list of functions that take no arguments.
- Run them in a `concurrent.futures.ThreadPoolExecutor` with `max_workers=workers`.
- Every time a job finishes, call `on_done(index, result)`, where `index` is the job's
  position in `funcs`. Calls happen in **completion order**, and they must be made from the
  **calling thread** (the thread that called `run_with_progress`), not from a worker thread,
  so `on_done` can safely print or update a progress bar without a lock.
- Return the list of results in **submission order** (the order of `funcs`).
- If a job raises, the exception propagates out of `run_with_progress` (no special handling).
- An empty `funcs` returns `[]` and never calls `on_done`.

**Example**

```python
import time

def job(name, seconds):
    def run():
        time.sleep(seconds)
        return name
    return run

funcs = [job("slow", 0.3), job("fast", 0.1), job("middle", 0.2)]
results = run_with_progress(funcs, 3, lambda i, r: print(f"done #{i}: {r}"))
print(results)
```

Output:

```text
done #1: fast
done #2: middle
done #0: slow
['slow', 'fast', 'middle']
```

The progress lines follow finishing time; the returned list follows the input.
