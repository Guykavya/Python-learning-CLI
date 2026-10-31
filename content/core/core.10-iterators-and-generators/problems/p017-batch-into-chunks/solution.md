## Approach

Make one iterator from the input. Then repeat: take up to `n` items with `islice` and put them
in a list. An empty list means the source is finished, so return. Otherwise yield the list.

Because we always cut from the **same** iterator `it`, each batch starts where the last one
stopped. If we used `islice(iterable, n)` on a list each time, we would get the first `n`
items again and again.

## Code

```python
from itertools import islice


def batches(iterable, n):
    if n < 1:
        raise ValueError("n must be at least 1")
    it = iter(iterable)
    while True:
        chunk = list(islice(it, n))
        if not chunk:
            return
        yield chunk
```

## Complexity

O(total items) time. Memory is O(n): only one batch is in memory at a time.

## Another way

A plain loop that fills a list and yields it when it reaches `n` items:

```python
def batches(iterable, n):
    if n < 1:
        raise ValueError("n must be at least 1")
    chunk = []
    for item in iterable:
        chunk.append(item)
        if len(chunk) == n:
            yield chunk
            chunk = []
    if chunk:
        yield chunk
```

Python 3.12 and newer also has `itertools.batched(iterable, n)`, which yields tuples.
