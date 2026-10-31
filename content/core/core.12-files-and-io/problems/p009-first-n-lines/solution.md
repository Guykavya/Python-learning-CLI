## Approach

Iterate over the file object. Python reads the file in small blocks, one line at a time, so stopping early reads almost nothing. `itertools.islice(f, n)` does the stopping for you. Remove only the newline with `rstrip("\n")`, so that spaces at the end of a line stay.

## Code

```python
from itertools import islice


def first_lines(path, n):
    with open(path, encoding="utf-8") as f:
        return [line.rstrip("\n") for line in islice(f, n)]
```

## Complexity

O(n) time and memory, no matter how large the file is.

## Another way

`f.readline()` n times in a loop works too, but you must stop at the empty string `""`, which means end of file.
