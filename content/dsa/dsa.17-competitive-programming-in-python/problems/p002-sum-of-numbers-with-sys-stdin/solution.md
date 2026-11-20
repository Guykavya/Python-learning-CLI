## Approach

Read everything once, split, convert, add.

```python
import sys

data = sys.stdin.read().split()
n = int(data[0])
print(sum(map(int, data[1:1 + n])))
```

Why it is fast: `sys.stdin.read()` is one call that copies the whole input into memory. `split()` and `map(int, ...)` run in C. The slow version calls `input()` `n` times, and each call goes through the Python layer, checks for `sys.stdout` flushing and strips the newline.

Example: for the input `3 / 5 / -2 / 10` the token list is `["3", "5", "-2", "10"]`; `data[1:4]` are the three numbers and `sum` gives 13.

## Complexity

`O(n)` time, `O(n)` memory for the token list (for 2·10^5 numbers this is a few megabytes).

## Another way

`sys.stdin.readline()` per line is much faster than `input()` and does not need the whole text in memory at once; use it when the input is huge or when you must react to each line (interactive problems). For plain "read everything" tasks, `read().split()` is the shortest and fastest.
