# How many workers?

Chapter sections 2.4 (the settings that matter), 2.5 (Uvicorn for ASGI apps) and "Try it: how many workers?". A **sync** Gunicorn worker handles one request at a time, so the number of workers is the number of requests in flight. The rule of thumb for CPU-bound code is `2 x CPU cores + 1`, but every worker loads your whole app, so **memory** can cap it. A `gthread` worker (`threads = 4`) can wait on 4 database calls at once. An async app on Uvicorn juggles many waiting requests in one process, so you start about one process per core.

## What to write

```python
def worker_plan(cpus: int, app_kind: str, memory_mb: int, mb_per_worker: int) -> dict: ...
```

`app_kind` is `"sync"`, `"threaded"` or `"async"`. Let `by_memory = memory_mb // mb_per_worker` (how many workers fit in memory). Return a dict with these four keys:

| `app_kind` | `server` | `workers` | `threads` | `concurrent` (requests in flight) |
|---|---|---|---|---|
| `sync` | `"gunicorn"` | `min(2 * cpus + 1, by_memory)` | `1` | `workers` |
| `threaded` | `"gunicorn"` | `min(2 * cpus + 1, by_memory)` | `4` | `workers * 4` |
| `async` | `"uvicorn"` | `min(cpus, by_memory)` | `None` | `None` (many per worker) |

Raise `ValueError` when `cpus < 1`, when `mb_per_worker <= 0`, when `app_kind` is not one of the three, or when `memory_mb < mb_per_worker` (not even one worker fits).

## Example

```python
worker_plan(4, "sync", 2048, 150)
# {'server': 'gunicorn', 'workers': 9, 'threads': 1, 'concurrent': 9}
worker_plan(4, "threaded", 2048, 150)
# {'server': 'gunicorn', 'workers': 9, 'threads': 4, 'concurrent': 36}   <- the chapter's "Try it": 9 workers become 36 requests
worker_plan(8, "sync", 1024, 300)
# {'server': 'gunicorn', 'workers': 3, 'threads': 1, 'concurrent': 3}    <- memory caps it: 17 would not fit
worker_plan(4, "async", 4096, 200)
# {'server': 'uvicorn', 'workers': 4, 'threads': None, 'concurrent': None}
```
