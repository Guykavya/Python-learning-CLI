## Approach

- `my_chain`: `yield from` each iterable in turn.
- `my_enumerate`: a counter next to a `for` loop.
- `my_zip`: turn each input into an iterator once, then build rows with `next()`. The first
  `StopIteration` ends everything. Because the row is built left to right, an item already taken
  from an earlier iterator is lost when a later one runs out, exactly like the real `zip`.
  With no inputs the `for` loop over iterators would build an empty row for ever, so return at once.
- `my_islice`: count positions. Yield when `position >= start`. Check the stop **after** yielding
  and before the `for` loop asks for the next item, so no extra item is read.

## Code

```python
from collections.abc import Iterable, Iterator


def my_chain(*iterables: Iterable[object]) -> Iterator[object]:
    for iterable in iterables:
        yield from iterable


def my_enumerate(iterable: Iterable[object], start: int = 0) -> Iterator[tuple[int, object]]:
    index = start
    for item in iterable:
        yield index, item
        index += 1


def my_zip(*iterables: Iterable[object]) -> Iterator[tuple[object, ...]]:
    if not iterables:
        return
    iterators = [iter(x) for x in iterables]
    while True:
        row = []
        for it in iterators:
            try:
                row.append(next(it))
            except StopIteration:
                return
        yield tuple(row)


def my_islice(iterable: Iterable[object], start: int, stop: int | None) -> Iterator[object]:
    if stop is not None and stop <= start:
        return
    position = 0
    for item in iterable:
        if position >= start:
            yield item
        position += 1
        if stop is not None and position >= stop:
            return
```

## Complexity

Each function does O(1) work per item and uses O(1) extra memory (`my_zip` uses O(k) for k inputs).

## Another way

`my_enumerate` can be `my_zip(itertools.count(start), iterable)`, and `my_islice` could use
`my_enumerate` to get positions. Composing small iterator tools like this is exactly how the real
`itertools` recipes are written. The real versions are written in C, so they are faster, but they
follow the same logic.
