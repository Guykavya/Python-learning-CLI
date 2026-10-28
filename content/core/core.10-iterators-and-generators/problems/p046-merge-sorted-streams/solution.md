## Approach

Sorted inputs mean the smallest unused item of each input is at its front. So the smallest item
overall is the smallest of the fronts. Keep one waiting item per input, yield the smallest, and
refill only that input. Scanning in input order with a strict `<` keeps ties in input order (the
merge is *stable*). Removing an input when it ends lets the others carry on.

Note: `for item in it: ... break` is a neat way to take "the first item, if there is one" without
catching `StopIteration`.

## Code

```python
from collections.abc import Callable, Iterable, Iterator


def merge_sorted(*iterables: Iterable[object], key: Callable[[object], object] | None = None) -> Iterator[object]:
    if key is None:
        key = lambda item: item

    waiting = []
    for iterable in iterables:
        it = iter(iterable)
        for item in it:
            waiting.append([item, it])
            break

    while waiting:
        best = 0
        for i in range(1, len(waiting)):
            if key(waiting[i][0]) < key(waiting[best][0]):
                best = i
        item, it = waiting[best]
        yield item
        try:
            waiting[best][0] = next(it)
        except StopIteration:
            waiting.pop(best)
```

## Complexity

With k inputs and n items in total: O(n * k) time, because each step scans k waiting items.
Memory O(k). That is fine for a few inputs.

## Another way

`heapq.merge(*iterables, key=...)` from the standard library does the same thing with a heap,
which finds the smallest in O(log k) instead of O(k). You will build a heap in the DSA track.
For two inputs only, a simpler version just compares the two fronts with `if a <= b`.
