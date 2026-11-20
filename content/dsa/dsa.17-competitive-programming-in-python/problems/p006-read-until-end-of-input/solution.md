## Approach

```python
import sys

out = []
total = 0
for line in sys.stdin:
    s = sum(map(int, line.split()))
    out.append(str(s))
    total += s
out.append(f"total: {total}")
print("\n".join(out))
```

`for line in sys.stdin` ends at EOF by itself. A last line without `\n` is still delivered. `str.split()` with no argument splits on any run of whitespace (spaces, tabs, `\r`) and ignores leading and trailing whitespace, so trailing spaces and `\r\n` cost nothing.

Example: the lines `"1 2\n"`, `"\n"`, `"3 \n"` give `3`, `0`, `3` and total `6`.

## Complexity

`O(total input size)`.

## Another way

`sys.stdin.read().splitlines()` first and loop over the list, which is what you do when you want to look at the whole input before answering.

Using `while True: line = input()` with `try/except EOFError` also works but is the slowest of the three.
