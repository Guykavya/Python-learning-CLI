## Hint 1

You cannot use a `for` loop over each iterable, because you only want **one** item from it
before moving on. What do you need instead of the iterables themselves? (Think `iter()`.)

## Hint 2

Keep a list of iterators that are still alive. In each round, call `next()` on each one. If
`next()` raises `StopIteration`, that iterator is finished: leave it out of the next round.
When is the list empty?

## Hint 3

```
alive = [iter(x) for x in iterables]
while alive:
    still_alive = []
    for it in alive:
        try: value = next(it)
        except StopIteration: continue
        still_alive.append(it)
        yield value
    alive = still_alive
```
