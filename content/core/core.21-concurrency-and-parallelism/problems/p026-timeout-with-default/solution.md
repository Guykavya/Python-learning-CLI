## Approach

`asyncio.timeout(seconds)` is an async context manager that sets an alarm. If the code
inside the block is still running when the alarm goes off, asyncio **cancels** the task at
its current `await` (a `CancelledError` is thrown in there), and when that cancellation
reaches the end of the block, the context manager turns it into a `TimeoutError`.

So:

- the slow coroutine really stops (its `except CancelledError` / `finally` blocks run);
- the caller sees an ordinary `TimeoutError` coming out of the `async with` line.

Catch exactly that `TimeoutError` **around** the block and return `default`. Anything else
(`ValueError`, ...) is not caught and propagates by itself.

## Code

```python
import asyncio


async def with_timeout(coro_fn, seconds, default):
    try:
        async with asyncio.timeout(seconds):
            return await coro_fn()
    except TimeoutError:
        return default
```

`return` inside the `async with` is fine: leaving the block normally just switches the alarm
off.

## Complexity

At most `seconds` of waiting plus the time the cancelled coroutine needs for its cleanup.
O(1) extra memory.

## Another way

`asyncio.wait_for(coro_fn(), timeout=seconds)` does the same in one call and also raises
`TimeoutError`:

```python
try:
    return await asyncio.wait_for(coro_fn(), seconds)
except TimeoutError:
    return default
```

`asyncio.timeout` is preferred in new code because one block can cover several awaits.

A subtle point for later: if `coro_fn` itself raises a `TimeoutError` (say, from a socket),
this code also returns `default`. To tell the two apart, keep the context manager in a name
(`cm = asyncio.timeout(seconds)`; `async with cm:`) and check `cm.expired()` in the `except`;
re-raise when it is `False`.
