## Hint 1

The starter calls `cpu_fn(job)` right inside the coroutine. While that call runs, can the
event loop run anything else? Which loop method hands a plain function to an executor and
gives you something you can `await`? How do you get the loop object from inside a coroutine?

## Hint 2

Start every job first (each `run_in_executor` call returns a future immediately), then wait for
all of them together, keeping their order.

```
loop = asyncio.get_running_loop()
futures = [loop.run_in_executor(executor, cpu_fn, job) for job in jobs]
return await asyncio.gather(*futures)
```
