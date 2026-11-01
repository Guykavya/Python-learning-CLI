# An async context manager that always closes

Opening a network session needs `await` (a handshake), and so does closing it. Plain `with`
cannot await, so async code uses `async with`, backed by an **async context manager**.

Write `session(log)` in `solution.py`, usable as `async with session(log) as s:`:

1. On enter: `await asyncio.sleep(0)` (stands for the handshake), append `"open"` to `log`,
   and give the body a state dict `{"open": True}` as `s`.
2. On exit: `await asyncio.sleep(0)` (stands for the goodbye message), set `s["open"]` to
   `False`, and append `"close"` to `log`.
3. The exit steps run **always**: after a normal body, when the body raises, and when the
   task is cancelled inside the body.
4. Errors from the body are **not swallowed**: they propagate after the close.

Use `@contextlib.asynccontextmanager` (or write a class with `__aenter__` and `__aexit__`).

**Example**

```python
import asyncio

async def main():
    log = []
    async with session(log) as s:
        log.append(f"use, open={s['open']}")
    print(log, s)

    log = []
    try:
        async with session(log) as s:
            raise ValueError("bad request")
    except ValueError as e:
        print("caught:", e)
    print(log)

asyncio.run(main())
```

Output:

```text
['open', 'use, open=True', 'close'] {'open': False}
caught: bad request
['open', 'close']
```
