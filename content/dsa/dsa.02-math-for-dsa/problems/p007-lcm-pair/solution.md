## Approach

`a = g * x` and `b = g * y` where `g = gcd(a, b)` and `x`, `y` have no common factor. The lcm is `g * x * y`,
which is `(a // g) * b`. Use `//` (exact integer division), not `/`, since `a // g` is always a whole number.

## Code

```python
q = int(input())
for _ in range(q):
    a, b = (int(x) for x in input().split())
    x, y = a, b
    while y:
        x, y = y, x % y
    print(a // x * b)
```

## Complexity

O(log min(a, b)) per pair. Python's integers grow as needed, so 36-digit answers are exact.

## Another way

`a * b // g` gives the same value in Python. The divide-first form `a // g * b` is the one to learn: in a
fixed-size integer language the product `a * b` can overflow even when the lcm itself would fit.
