## Hint 1

`async with asyncio.timeout(seconds):` cancels whatever is being awaited inside it when the
time is up, and turns that cancellation into a `TimeoutError` when the block exits. Where
should the `try` / `except TimeoutError` go: inside the block or around it?

## Hint 2

The `TimeoutError` comes out of the `async with` statement itself, so the `try` must wrap
the whole block.

```
try:
    async with asyncio.timeout(seconds):
        return await coro_fn()
except TimeoutError:
    return default
```

Other exceptions are not caught, so they propagate on their own.
