## Approach

`deque(iterable, maxlen=n)` is a ready-made "keep the last n" machine. It walks the iterable
once; every new item is appended on the right, and when the deque already holds `n` items the
oldest one falls off the left. At the end it holds exactly the last `n` items in order.

Because it only needs an iterable, `last_n` works the same for a list, a generator or an open
file. `tail` opens the file in **text mode** with `encoding="utf-8"`; text mode reads `\r\n` as
`\n` (universal newlines), so one `rstrip("\n")` cleans every line on every platform.

`deque` itself raises `ValueError` for a negative `maxlen`, but checking first gives a clearer
message.

## Code

```python
from collections import deque
from collections.abc import Iterable
from pathlib import Path


def last_n(items: Iterable[str], n: int) -> list[str]:
    if n < 0:
        raise ValueError(f"n must be >= 0, got {n}")
    return list(deque(items, maxlen=n))


def tail(path: str | Path, n: int = 10) -> list[str]:
    with open(path, encoding="utf-8") as f:
        lines = last_n(f, n)
    return [line.rstrip("\n") for line in lines]
```

## Complexity

O(L) time for L lines read (each append is O(1)), O(n) memory, no matter how big the file is.

## Another way

`f.readlines()[-n:]` gives the same answer for small files but holds the whole file in memory
(and `[-0:]` is the **whole** list, so `n = 0` needs a special case). The real `tail` program goes
further: it seeks near the end of the file and reads backwards in blocks, so it does not even read
the beginning. That is faster for huge files but much more code; the deque version is the right
first tool.
