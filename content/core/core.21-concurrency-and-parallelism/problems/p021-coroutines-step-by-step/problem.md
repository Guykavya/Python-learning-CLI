# Trace: coroutines step by step

Three facts to keep in mind:

- Calling an `async def` function does **not** run its body. It only creates a **coroutine
  object**, a paused function waiting to be started.
- `await coro` runs that coroutine **now**, until it finishes, and gives back its return
  value. While it is paused at its own `await`, the event loop may run *other* tasks, but this
  program has no other tasks.
- `asyncio.run(coro)` starts an event loop, runs the coroutine to the end, closes the loop and
  returns the coroutine's return value.

What does this program print?

```python
import asyncio


async def greet(name):
    print("greet start", name)
    await asyncio.sleep(0)
    print("greet end", name)
    return f"hi {name}"


async def main():
    print("main start")
    c = greet("A")
    print("made", type(c).__name__)
    result = await c
    print("result:", result)
    r1 = await greet("B")
    r2 = await greet("C")
    print(r1, "|", r2)
    print("main end")
    return 42


print("before run")
coro = main()
print("main() gave a", type(coro).__name__)
value = asyncio.run(coro)
print("run returned", value)
```

**Example**: the first line is `before run`. Nothing above it prints: the two `async def`
statements only define functions.

Write in `answer.txt` the lines the program prints, in order.
