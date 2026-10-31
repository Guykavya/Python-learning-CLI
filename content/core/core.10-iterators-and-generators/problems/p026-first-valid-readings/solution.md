## Approach

A pipeline of three lazy stages:

1. `chain(*sources)` makes one stream from all sources, in order. It opens a source only when
   the one before it is finished.
2. A generator expression keeps the valid readings.
3. `islice(valid, n)` stops after `n` items without asking for one more.

`list(...)` pulls items through the pipeline until `islice` stops. So the next source is never
touched if the first ones already gave `n` readings.

## Code

```python
from itertools import chain, islice


def first_valid(sources, n):
    readings = chain(*sources)
    valid = (r for r in readings if r is not None and 0 <= r <= 50)
    return list(islice(valid, n))
```

## Complexity

O(number of readings read) time; O(n) memory for the result.

## Another way

`chain.from_iterable(sources)` does the same as `chain(*sources)`. It is better when `sources`
is itself a generator or very long, because `*sources` must unpack all of them first.

A nested loop also works: `for source in sources: for r in source: ...`, appending valid values
and returning as soon as the list has `n` items. Return **before** the outer loop moves on.
