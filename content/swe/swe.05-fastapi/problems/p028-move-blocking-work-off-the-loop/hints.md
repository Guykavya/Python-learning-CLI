## Hint 1

While `make_report` sleeps, which thread is stuck? In an `async def` endpoint it is the event-loop thread, the one that should be starting the other two requests. How can an `async def` wait for a blocking function *without* running it itself? (Section 10.3.)

## Hint 2

`asyncio.to_thread(func, *args)` runs `func(*args)` in a worker thread and gives you something to `await`. While you await it, the loop is free. Remember the `await`: without it you return a coroutine object, not the report.

## Hint 3

```text
@app.get("/report/{n}")
async def report(n: int):
    return await asyncio.to_thread(make_report, n)
```
