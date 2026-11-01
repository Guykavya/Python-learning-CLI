## Approach

`@asynccontextmanager` turns an async generator with **one** `yield` into an async context
manager:

| Your function | `async with session(log) as s:` |
|---|---|
| code before `yield` | runs on enter (`__aenter__`) |
| the yielded value | becomes `s` |
| code after `yield` | runs on exit (`__aexit__`) |

On exit, if the body raised (or the task was cancelled), that exception is **thrown into
your function at the `yield`**. A plain `yield` followed by cleanup lines is therefore not
enough: the exception skips the lines. Wrapping the `yield` in `try/finally` runs the cleanup
in every case, and because there is no `except`, the exception continues to the caller after
the `finally`. That one shape gives all four rules.

## Code

```python
import asyncio
from contextlib import asynccontextmanager


@asynccontextmanager
async def session(log):
    await asyncio.sleep(0)
    log.append("open")
    state = {"open": True}
    try:
        yield state
    finally:
        await asyncio.sleep(0)
        state["open"] = False
        log.append("close")
```

The `try` starts **after** the open steps: if opening fails, there is nothing to close.

## Complexity

O(1) time and memory per use.

## Another way

The same thing as a class:

```python
class session:
    def __init__(self, log):
        self.log = log

    async def __aenter__(self):
        await asyncio.sleep(0)
        self.log.append("open")
        self.state = {"open": True}
        return self.state

    async def __aexit__(self, exc_type, exc, tb):
        await asyncio.sleep(0)
        self.state["open"] = False
        self.log.append("close")
        return False          # False (or None): do not swallow the exception
```

`__aexit__` is called in every case, so it needs no `try/finally`. Returning a true value
from it would **swallow** the body's exception, which is almost never what you want.

Awaiting inside `finally` while being cancelled (the `sleep(0)` there) works here; a cleanup
that may take long should be short or protected, because a second cancel can interrupt it.
