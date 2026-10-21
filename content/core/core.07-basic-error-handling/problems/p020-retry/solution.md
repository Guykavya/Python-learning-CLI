## Approach

A counted loop around one `try`. A success returns at once. A listed failure is remembered in
`last_error`, because `e` is deleted when the handler ends. Exceptions not listed in `errors` do
not match the clause and propagate on the first attempt. After the loop, every attempt has failed,
and `raise last_error` re-raises the last one.

## Code

```python
def retry(func, attempts=3, errors=(ValueError,)):
    """Call func() up to `attempts` times, retrying only the given error types."""
    if attempts < 1:
        raise ValueError("attempts must be at least 1")
    last_error = None
    for _ in range(attempts):
        try:
            return func()
        except errors as e:
            last_error = e
    raise last_error
```

## Complexity

At most `attempts` calls to `func`.

## Another way

Make the last attempt outside the loop: loop `attempts - 1` times catching errors, then
`return func()` with no `try`, so the last failure propagates naturally with a clean traceback.
Real retry helpers also wait between attempts (`time.sleep`), often doubling the wait each time
("exponential backoff").
