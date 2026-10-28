## Hint 1

Why can't `longest` use a plain `T`? Think about the body: `len(item)`. What does a checker know about an unbounded `T`? Which argument of `TypeVar(...)` limits "any type" to "any type with a length"?

## Hint 2

`TypeVar("S", bound=Sized)`. The input may be any iterable (even a one-shot iterator), so walk it once. Keep the best item so far; replace it only when the new length is **strictly** larger (or smaller), so that ties keep the first. How do you start when you have no item yet?

## Hint 3

```
S = TypeVar("S", bound=Sized)

def longest(items):
    best = None; have = False
    for item in items:
        if not have or len(item) > len(best): best = item; have = True
    if not have: raise ValueError("longest() of empty iterable")
    return best

shortest: the same with <.
longest_or_none: try longest, or check "have" and return None.
```
(Note `best = None` needs care for the checker; a sentinel flag or `next(iterator)` for the first item avoids it.)
