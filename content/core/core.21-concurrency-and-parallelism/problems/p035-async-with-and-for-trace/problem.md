# Trace: async with and async for, step by step

`async with` and `async for` are the async versions of `with` and `for`. The rules are the same
as the sync ones you already know, but every step can `await`:

- `async with X as v:` runs `await X.__aenter__()` and binds its **return value** to `v`. When
  the block ends (normally or with an exception) it runs `await X.__aexit__(exc_type, exc, tb)`.
  If `__aexit__` returns a **true** value, the exception is swallowed; otherwise it continues.
- `async for x in agen:` runs the async generator up to its next `yield` each time round. When
  the generator body ends, the loop ends.
- If you `break` out of an `async for`, the generator is **paused, not finished**: its
  `finally` has not run yet. `await agen.aclose()` throws `GeneratorExit` into it at the paused
  `yield`, so its `finally` runs then.

What does this program print?

```python
import asyncio


class Door:
    def __init__(self, name):
        self.name = name

    async def __aenter__(self):
        print(f"enter {self.name}")
        await asyncio.sleep(0)
        return self.name.upper()

    async def __aexit__(self, exc_type, exc, tb):
        kind = exc_type.__name__ if exc_type else None
        print(f"exit {self.name} {kind}")
        return exc_type is KeyError          # True swallows the exception


async def numbers(n):
    try:
        for i in range(n):
            print(f"yield {i}")
            yield i
        print("generator finished")
    finally:
        print("generator cleanup")


async def main():
    async with Door("a") as d:
        print("body", d)

    try:
        async with Door("b"):
            print("body b")
            raise ValueError("bad")
    except ValueError as e:
        print("caught", e)

    async with Door("c"):
        raise KeyError("k")
    print("after c")

    async for x in numbers(2):
        print("got", x)

    gen = numbers(5)
    async for x in gen:
        print("got", x)
        if x == 1:
            break
    print("after break")
    await gen.aclose()
    print("closed")


asyncio.run(main())
```

**Example**: the first three lines are

```text
enter a
body A
exit a None
```

`__aenter__` prints `enter a` and returns `"A"`, which `as d` binds. The body prints it. The
block ends without an exception, so `__aexit__` gets `exc_type = None`.

Write in `answer.txt` the lines the program prints, in order.
