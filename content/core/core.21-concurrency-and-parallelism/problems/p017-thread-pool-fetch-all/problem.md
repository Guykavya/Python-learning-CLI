# Fetch everything with a thread pool

`concurrent.futures.ThreadPoolExecutor` keeps a fixed number of worker threads and a queue of
jobs, so you do not manage threads yourself:

- `executor.submit(fn, arg)` puts a job on the queue and returns a **`Future`** at once: a
  placeholder for a result that does not exist yet.
- `as_completed(futures)` yields each future **as soon as it finishes**.
- `future.result()` returns the value, or **re-raises** the exception that `fn` raised in the
  worker thread.

Write `fetch_all(urls, fetch, workers)`:

- `fetch(url)` is a blocking function (for example, an HTTP request). It may raise.
- Run `fetch` for every URL in a `ThreadPoolExecutor(max_workers=workers)` using `submit`, and
  collect results with `as_completed`.
- Return a dict mapping each URL to `fetch(url)`'s return value, **or to the exception object**
  if it raised. One failure must not stop the others.

You can assume the URLs are all different.

**Example**

```python
import time

def fake_fetch(url):
    time.sleep(0.2)
    if "bad" in url:
        raise ConnectionError(f"cannot reach {url}")
    return len(url)

start = time.perf_counter()
result = fetch_all(["a.com", "bad.org", "python.org"], fake_fetch, workers=3)
print(result)
print(round(time.perf_counter() - start, 1))
```

```text
{'a.com': 5, 'bad.org': ConnectionError('cannot reach bad.org'), 'python.org': 10}
0.2
```

(The order of keys in your dict may differ: it follows completion order. Your time will differ
a little.)
