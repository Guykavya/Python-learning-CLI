# Round-robin: take turns between streams

A music app plays songs from several playlists by **taking turns**: one song from the first
list, one from the second, one from the third, then back to the first. When a playlist runs
out, it is skipped. Play stops when every list is empty.

Write a **generator function** `round_robin(*iterables)` in `solution.py` that does this for
any number of iterables.

Rules that the tests check:

1. It is a generator and works when some iterables are **endless**.
2. It reads from a source only when it is that source's turn.

**Example**

```python
list(round_robin("abc", "d", "ef"))      # ['a', 'd', 'e', 'b', 'f', 'c']
list(round_robin([1, 2], [], [3]))       # [1, 3, 2]
list(round_robin())                      # []

from itertools import count, islice
list(islice(round_robin([1, 2], count(100)), 6))   # [1, 100, 2, 101, 102, 103]
```
