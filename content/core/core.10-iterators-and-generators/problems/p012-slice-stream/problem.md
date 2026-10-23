# slice_stream with islice

Lists support `items[start:stop]`. Generators do not. `itertools.islice(iterable, start, stop)` does the same
job lazily.

Write `slice_stream(iterable, start, stop)` in `solution.py`. It returns a **list** with the items at
positions `start` up to (not including) `stop`, counted from 0. It must work on infinite iterables, and it
must not read items beyond position `stop - 1`.

**Examples**

```python
slice_stream(range(100), 3, 6)       # [3, 4, 5]
slice_stream("abcdef", 0, 2)         # ["a", "b"]
slice_stream([1, 2], 5, 9)           # []
```
