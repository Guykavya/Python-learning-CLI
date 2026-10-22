## Approach

`chain.from_iterable(xs)` goes through `xs` and yields every item of every inner iterable, one after another. It does not copy anything until you ask for the items.

## Code

```python
from itertools import chain


def flatten_once(list_of_lists):
    return list(chain.from_iterable(list_of_lists))
```

## Complexity

O(total items).

## Another way

A nested comprehension does the same: `[x for inner in list_of_lists for x in inner]`. `chain` is lazy, so you can also use it without `list()`.
