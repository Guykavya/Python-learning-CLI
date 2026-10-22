## Approach

`islice` walks through the iterable once. It has to read and throw away the first `start` items (an iterator cannot jump), but it stops as soon as it reaches `stop`.

## Code

```python
from itertools import islice


def slice_stream(iterable, start, stop):
    return list(islice(iterable, start, stop))
```

## Complexity

O(stop) time, O(stop - start) memory for the result.

## Another way

For a list you can slice directly. `islice` is for iterators and generators, where slicing with `[]` is a `TypeError`.
