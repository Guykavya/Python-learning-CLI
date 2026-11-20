## Approach

Token-based reading ignores line breaks and blank lines.

```python
import sys

it = iter(sys.stdin.read().split())
t = int(next(it))
out = []
for _ in range(t):
    n = int(next(it))
    a = [int(next(it)) for _ in range(n)]
    total = sum(a)
    out.append(str(sum(1 for x in a if x * n > total)))
print("\n".join(out))
```

Check on the example: first case `n = 3`, `a = [1, 2, 6]`, `total = 9`; `1*3 = 3`, `2*3 = 6`, `6*3 = 18`: only `18 > 9`, so 1. Second case `[5,5,5,5]`, total 20: `5*4 = 20`, not strictly greater, so 0.

## Complexity

`O(sum of n)` in total.

## Another way

Keep the variable `pos` and read `data[pos]`, `pos += 1`. An iterator is shorter; an index lets you jump back if you ever need to.

## Trap that this problem tests

A solution that reads `n = int(input())` and then `input().split()` works only when the numbers are on exactly one line and there are no blank lines. The tests include a messy file where the numbers of one test case span three lines.
