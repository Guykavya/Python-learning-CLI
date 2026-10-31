## Approach

Turn every input into an iterator once. Then work in rounds. In each round, ask every live
iterator for one item with `next()`. An iterator that raises `StopIteration` is done; we do not
keep it for the next round. The loop ends when no iterator is left.

Because we yield right after each `next()`, nothing is read before it is needed, so endless
sources are fine.

## Code

```python
def round_robin(*iterables):
    alive = [iter(x) for x in iterables]
    while alive:
        still_alive = []
        for it in alive:
            try:
                value = next(it)
            except StopIteration:
                continue
            still_alive.append(it)
            yield value
        alive = still_alive
```

## Complexity

O(total number of items + number of iterables) time. O(number of iterables) memory.

## Another way

`zip_longest(*iterables, fillvalue=marker)` with a unique `marker = object()` gives the rounds
as tuples. Flatten them and drop the markers. It is shorter, but it reads a whole round from
every source before yielding the first item of that round, and it cannot use `None` as the marker
if `None` is a real value.
