## Hint 1

The event loop runs in **one** thread. A function that blocks that thread (with
`time.sleep`, a blocking socket, a big calculation) stops every task. Where else could the
blocking call run, so that the loop's thread is free? What does `await
asyncio.to_thread(func, arg)` give back?

## Hint 2

`asyncio.to_thread(func, *args)` runs `func(*args)` in a worker thread and returns an
awaitable; awaiting it pauses only **your** task. To run all lookups at the same time,
create all those awaitables and `gather` them.

```
return list(await gather(*(to_thread(slow_lookup, r) for r in requests)))
```

Pass the function and its argument separately: `to_thread(slow_lookup, r)`, not
`to_thread(slow_lookup(r))`.
