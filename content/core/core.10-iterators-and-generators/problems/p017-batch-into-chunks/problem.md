# Batch a stream into chunks of n

A web service accepts at most `n` records per request. You have a long stream of records,
maybe from a generator, maybe endless. You must send them in groups.

Write a **generator function** `batches(iterable, n)` in `solution.py`. It yields lists of
`n` items, in order. The last list may be shorter. It never yields an empty list.

Rules that the tests check:

1. It is a generator: calling it runs nothing, and items come one batch at a time.
2. It works on an **endless** input. Never call `list()` on the whole input.
3. To build one batch it reads **at most `n`** items from the source.
4. If `n` is smaller than 1, raise `ValueError`. (Because this is a generator, the error
   appears at the first `next()`, not at the call. That is fine.)

**Example**

```python
list(batches([1, 2, 3, 4, 5, 6, 7], 3))   # [[1, 2, 3], [4, 5, 6], [7]]
list(batches(range(4), 2))                # [[0, 1], [2, 3]]   no empty list at the end
list(batches([], 5))                      # []

from itertools import count, islice
list(islice(batches(count(), 2), 3))      # [[0, 1], [2, 3], [4, 5]]
```
