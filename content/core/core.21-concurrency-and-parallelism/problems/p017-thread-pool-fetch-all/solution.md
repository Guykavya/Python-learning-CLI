## Approach

1. Open the pool with `with`, so its threads are shut down (and waited for) at the end.
2. **Submit every job first.** Each `submit` returns a `Future` immediately; the pool's
   threads start working in the background. Keep a dict `future -> url`, because a finished
   future does not tell you which URL it was for.
3. Loop over `as_completed(...)`: each future arrives as soon as it is done. `future.result()`
   returns the value or **re-raises** the worker's exception, so wrap it in `try/except` and
   store the exception object.

Compare with p004: there you had to catch errors inside the thread yourself. A `Future`
captures the exception for you and hands it over when you ask for the result.

## Code

```python
from concurrent.futures import ThreadPoolExecutor, as_completed


def fetch_all(urls, fetch, workers):
    results = {}
    with ThreadPoolExecutor(max_workers=workers) as executor:
        future_to_url = {executor.submit(fetch, url): url for url in urls}
        for future in as_completed(future_to_url):
            url = future_to_url[future]
            try:
                results[url] = future.result()
            except Exception as exc:
                results[url] = exc
    return results
```

## Complexity

n jobs on `workers` threads: about `ceil(n / workers)` rounds of fetch time when fetches wait
on the network. Only `workers` threads exist, however long the list. `as_completed` lets you
handle (print, save) each result as soon as it is ready instead of waiting for the slowest.

## Another way

`executor.map(fetch, urls)` is shorter and returns results in **input** order, but the first
exception is raised from the iterator as soon as you reach that item, and the remaining results
are lost unless you wrap `fetch` in a function that catches errors. With `submit` and
`as_completed` you control each future separately.

`concurrent.futures.wait(futures, return_when=FIRST_EXCEPTION)` is useful when one failure
should stop everything (p041).
