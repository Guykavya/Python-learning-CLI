## Approach

When a generator's body ends with `return value`, Python raises `StopIteration(value)`. The value
lives in the exception. `for` and `list()` catch `StopIteration` quietly, so they cannot give the
value back. To see it, `drain` must drive the iterator with `next()` and catch the exception itself.
A plain iterator such as a list iterator raises `StopIteration()` with no value, so `e.value` is `None`.

`counted` is an ordinary loop with a counter, and `return n` after the loop. Inside another
generator, `n = yield from counted(...)` receives that number, which is how a sub-generator reports
a result to its parent.

## Code

```python
from collections.abc import Iterable, Iterator


def counted(iterable: Iterable[object]) -> Iterator[object]:
    n = 0
    for item in iterable:
        n += 1
        yield item
    return n


def drain(iterator: Iterator[object]) -> tuple[list[object], object]:
    items = []
    while True:
        try:
            items.append(next(iterator))
        except StopIteration as e:
            return items, e.value
```

## Complexity

O(n) time. `counted` uses O(1) memory; `drain` stores all n items.

## Another way

`yield from` also catches the return value, so a small inner generator can do the work:

```python
def drain(iterator):
    box = []

    def collect():
        result = yield from iterator
        box.append(result)     # runs once, after the last item

    items = list(collect())
    return items, box[0]
```

It works, but it is harder to read than the plain `while`/`next` loop, so prefer the loop.
For a plain iterator such as `iter([7, 8])`, `yield from` also gives `None`.
