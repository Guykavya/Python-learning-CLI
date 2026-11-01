## Hint 1

`await fetch(name)` inside a `for` loop waits for each fetch to finish before even starting
the next. How can you **create** all the coroutines first and then wait for all of them
together?

## Hint 2

`asyncio.gather(*coros)` wraps each coroutine in a task, runs them all, and returns their
results in the order you passed them in (not in finishing order).

```
coros = [fetch(name) for name in names]     # nothing runs yet
return list(await asyncio.gather(*coros))   # all run together
```
