# retry: try again when a call fails

Network calls fail now and then. A common fix is to **try again** a few times before giving up.
Write a decorator factory `retry` in `solution.py`:

```python
retry(attempts, exceptions=(Exception,), delay=0.0, sleep=time.sleep)
```

The decorated function behaves like this:

1. Call the function. If it returns, return its result.
2. If it raises an exception that matches `exceptions`, call `sleep(delay)` and try again.
3. Make **at most `attempts` calls in total**. If the last call also fails, **re-raise that
   last exception** (the original one, not a new one).
4. Do **not** sleep after the last failed attempt: there is nothing to wait for.
5. An exception that does **not** match `exceptions` is raised at once: no sleep, no retry.
6. `exceptions` can be one exception class or a tuple of classes, like in an `except` clause.
7. `attempts` smaller than 1 is a mistake: raise `ValueError` when `retry(...)` is called,
   before any function is decorated.
8. Pass all positional and keyword arguments through, and keep the name and docstring with
   `functools.wraps`.

Why the `sleep` parameter? Tests must not really wait. The tests pass their own `sleep`
function that only writes down the delay. In real code you leave the default, `time.sleep`.

**Example**

```python
waits = []

@retry(3, exceptions=ConnectionError, delay=0.5, sleep=waits.append)
def fetch(url):
    ...   # fails twice with ConnectionError, then returns "page"

fetch("x.org")   # "page"
waits            # [0.5, 0.5]   two failures, two waits
```

If `fetch` failed all three times, the third `ConnectionError` is raised, and `waits` is still
`[0.5, 0.5]`.
