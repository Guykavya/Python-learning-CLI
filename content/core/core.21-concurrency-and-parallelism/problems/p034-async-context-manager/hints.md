## Hint 1

With `@asynccontextmanager`, you write an `async def` with exactly one `yield`. The code
before `yield` is the enter step, the value you yield becomes `s`, and the code after `yield`
is the exit step. When the body raises, where does that exception appear inside your
function? What does that do to the lines after `yield`?

## Hint 2

The body's exception (and a cancel) is thrown in **at the `yield`**. So the exit steps must
be in a `finally` around the `yield`. Do not add an `except`: then the error keeps
propagating by itself.

```
@asynccontextmanager
async def session(log):
    await sleep(0); log.append("open")
    state = {"open": True}
    try:
        yield state
    finally:
        await sleep(0); state["open"] = False; log.append("close")
```
