# Heavy work from async code with run_in_executor

An async web service receives image jobs. Making a thumbnail is a plain, **blocking** function
(CPU work in a C library, or a sync library you cannot change). If an `async def` calls it
directly, the whole event loop stops for the duration: no other request is served, no
heartbeat is sent.

`loop.run_in_executor(executor, func, arg)` runs `func(arg)` on an executor's thread (or
process) and gives back an awaitable. The loop stays free while the work runs elsewhere.

Write `async def handle_jobs(jobs, cpu_fn, executor) -> list`:

- run `cpu_fn(job)` for every job **on the given `executor`** (use
  `asyncio.get_running_loop().run_in_executor`),
- run them concurrently (as many at once as the executor allows),
- return the results in the order of `jobs`,
- if any `cpu_fn` call raises, let that exception propagate.

The event loop must stay responsive the whole time. The tests run a heartbeat task next to
your function and count its ticks.

**Example**

```python
def thumbnail(size):           # blocking: 0.1 s each
    time.sleep(0.1)
    return size // 2

with ThreadPoolExecutor(max_workers=4) as pool:
    asyncio.run(handle_jobs([800, 640, 1024, 320], thumbnail, pool))
# [400, 320, 512, 160]   after about 0.1 s, not 0.4 s
```

For real CPU-heavy Python code you would pass a `ProcessPoolExecutor` instead (threads share
one GIL); the function must then be defined at the top level of a module so it can be
pickled. The code of `handle_jobs` is the same for both.
