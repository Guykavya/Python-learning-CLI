## Approach

`asyncio.gather` has two modes:

- default: the first exception is raised out of `await gather(...)`. The other tasks keep
  running in the background, but you never see their results.
- `return_exceptions=True`: nothing is raised. The result list has one slot per awaitable,
  in argument order, holding **either the value or the exception object**.

The second mode is exactly a report. Walk `ids` and the results together with `zip`, and
sort each slot into `ok` or `failed` with `isinstance(result, BaseException)`.

Why `isinstance` and not `if result:`? A fetch may legally return `0`, `None`, `""` or
`[]`. Those are falsy but they are successes. Only an exception object is a failure.

(Why `BaseException` and not `Exception`? In gather's result a cancelled child shows up as a
`CancelledError` object, which is a `BaseException` but not an `Exception`. Counting it as a
failure is the safer choice.)

## Code

```python
import asyncio


async def fetch_report(ids, fetch):
    results = await asyncio.gather(*(fetch(i) for i in ids), return_exceptions=True)
    ok, failed = {}, {}
    for item_id, result in zip(ids, results):
        if isinstance(result, BaseException):
            failed[item_id] = type(result).__name__
        else:
            ok[item_id] = result
    return ok, failed
```

## Complexity

Wall time is the slowest fetch. One pass over the results: O(n) time and memory.

## Another way

Wrap each fetch so it never raises, and gather the wrappers:

```python
async def safe(item_id):
    try:
        return item_id, True, await fetch(item_id)
    except Exception as exc:
        return item_id, False, type(exc).__name__
```

This is more code, but you decide exactly which exceptions count as failures (here
`Exception` only, so a cancellation still propagates). Also note the weakness of
`return_exceptions=True`: a function that *returns* an exception object looks just like one
that raised it.
