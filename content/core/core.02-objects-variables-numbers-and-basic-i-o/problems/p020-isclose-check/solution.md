## Approach

Print both comparisons side by side to see where `==` fails and `isclose` succeeds.

## Code

```python
import math

a = float(input())
b = float(input())
c = float(input())
print("Exact:", a + b == c)
print("Close:", math.isclose(a + b, c, abs_tol=1e-9))
```

## Why each case comes out the way it does

- `0.5 + 0.25 == 0.75` is exactly `True`: those are powers of two, which binary stores exactly.
- `1e16 + 1 == 1e16` is `True`: at that size, neighbouring floats are 2 apart, so the `+ 1` is lost.
- `1e-12` vs `0`: the relative test alone says "not close" because zero has no size to compare against.
  `abs_tol=1e-9` accepts any difference smaller than one billionth.

## Another way

`abs((a + b) - c) < 1e-9` is a hand-written absolute test. It fails for very large numbers,
which is why `isclose` mixes relative and absolute tolerance.
