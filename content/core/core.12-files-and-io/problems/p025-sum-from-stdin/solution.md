## Approach

Loop with `for line in sys.stdin`. Python reads the input in small pieces, which also works for endless pipes. Strip each line; skip it if empty; otherwise `int()` it and add. Use `sys.stdin` inside the function (`import sys`, not `from sys import stdin`), because the object is looked up at call time and can be replaced.

## Code

```python
import sys


def total_from_stdin():
    total = 0
    for line in sys.stdin:
        line = line.strip()
        if line == "":
            continue
        total += int(line)
    print(f"total: {total}")
    return total
```

## Complexity

O(n) time, O(1) memory.

## Another way

`input()` reads one line at a time too, but it raises `EOFError` at the end, so you need a `try/except`. `sys.stdin.read()` loads everything at once. For big inputs, the `for` loop is best.
