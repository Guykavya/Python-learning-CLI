## Approach

```python
def worker_plan(cpus, app_kind, memory_mb, mb_per_worker):
    if cpus < 1:
        raise ValueError(f"cpus must be at least 1, got {cpus}")
    if mb_per_worker <= 0:
        raise ValueError(f"mb_per_worker must be positive, got {mb_per_worker}")
    if app_kind not in ("sync", "threaded", "async"):
        raise ValueError(f"app_kind must be 'sync', 'threaded' or 'async', got {app_kind!r}")
    if memory_mb < mb_per_worker:
        raise ValueError(f"{memory_mb} MB is not enough for even one worker of {mb_per_worker} MB")
    by_memory = memory_mb // mb_per_worker
    if app_kind == "async":
        return {"server": "uvicorn", "workers": min(cpus, by_memory), "threads": None, "concurrent": None}
    workers = min(2 * cpus + 1, by_memory)
    threads = 1 if app_kind == "sync" else 4
    return {"server": "gunicorn", "workers": workers, "threads": threads, "concurrent": workers * threads}
```

The CPU rule gives a starting point; memory gives a hard ceiling (each worker is a full copy of your app); threads or async turn "waiting for the database" into useful concurrency.

## Complexity

O(1). The thinking is in the formula: `2 x cores + 1` suits CPU-bound sync code, **not** I/O-bound code (chapter 2.4).

## Another way

Start from measurements instead of a formula: run a load test, watch CPU and memory, and raise workers or threads until throughput stops growing or memory runs out. With a connection pool, also check that `workers x threads` does not exceed the database's connection limit.
