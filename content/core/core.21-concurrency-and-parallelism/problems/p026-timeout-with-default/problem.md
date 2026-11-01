# A timeout with a fallback value

A weather widget asks a slow service for the temperature. If the answer takes longer than
half a second, the widget should show `"n/a"` instead of hanging.

Write `async def with_timeout(coro_fn, seconds, default)` in `solution.py`:

- `coro_fn` is an `async def` function with no arguments. Call it and await the result,
  but give it at most `seconds` seconds.
- If it finishes in time, return its result (even if that result is `0`, `None` or `""`).
- If the time runs out, the slow call must be **cancelled** (not left running) and
  `with_timeout` returns `default`.
- If `coro_fn` raises any other error (for example `ValueError`), let that error propagate.
  Only the timeout turns into `default`.

Use `async with asyncio.timeout(seconds):`.

**Example**

```python
import asyncio

async def quick():
    await asyncio.sleep(0.01)
    return 21

async def slow():
    await asyncio.sleep(10)
    return 99

print(asyncio.run(with_timeout(quick, 0.5, "n/a")))   # 21
print(asyncio.run(with_timeout(slow, 0.1, "n/a")))    # n/a   (after about 0.1 s)
```
