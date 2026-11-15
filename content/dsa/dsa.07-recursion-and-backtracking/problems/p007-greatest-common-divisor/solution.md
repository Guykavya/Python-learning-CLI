## Approach

Every common divisor of `a` and `b` also divides `a % b = a - q*b`, and the other way round, so `gcd(a, b) = gcd(b, a % b)`. The second number gets strictly smaller (`a % b < b`), so it reaches 0, and `gcd(a, 0) = a`.

## Code

```python
def gcd(a, b):
    if b == 0:
        return a
    return gcd(b, a % b)
```

## Complexity

`O(log(min(a, b)))` steps: every two steps the larger number at least halves. The worst case is two neighbouring Fibonacci numbers.

## Another way

The same rule as a loop: `while b: a, b = b, a % b`, then `return a`. That is what `math.gcd` does (in C).
