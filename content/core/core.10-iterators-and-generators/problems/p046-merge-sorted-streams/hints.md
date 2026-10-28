## Hint 1

At any moment, what do you need to know about each input to decide what comes next? Only its
**first unused item**. Keep one "waiting" item per input. Which one do you yield?

## Hint 2

Keep a list of `[waiting_item, iterator]` pairs in input order. Find the index of the smallest
`key(waiting_item)`, using `<` so the earliest one wins ties. Yield it, then replace it with
`next(iterator)`; if that raises `StopIteration`, remove the pair.

## Hint 3

```
if key is None: key = lambda x: x
waiting = []
for each iterable:
    it = iter(iterable)
    take its first item (if any) -> waiting.append([item, it])
while waiting:
    best = index of smallest key in waiting (first one on ties)
    yield waiting[best][0]
    try: waiting[best][0] = next(waiting[best][1])
    except StopIteration: waiting.pop(best)
```
