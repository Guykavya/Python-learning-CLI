## Hint 1

Find the two places where an `async def` function is **called without** `await` or
`asyncio.run`: `coro = main()` and `c = greet("A")`. What runs at those lines, and what does
`type(...).__name__` say about the object you get back?

## Hint 2

Mark when each body really starts:

```
main()            -> creates a coroutine, body NOT run yet
asyncio.run(coro) -> main's body starts here
greet("A")        -> creates a coroutine, body NOT run yet
await c           -> greet A runs start..end, gives "hi A"
await greet("B")  -> B runs fully before the next line
await greet("C")  -> then C runs fully
```

Does `await asyncio.sleep(0)` let anything else run in between, when there are no other
tasks?
