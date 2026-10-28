## Approach

Each function is one exact integer tool:

- Handshakes are unordered pairs: `comb(n, 2) = n(n-1)/2`.
- Podiums are ordered choices: `perm(n, k) = n * (n-1) * ... * (n-k+1)`. Both return `0` when
  `k > n`.
- Lowest terms: divide by the greatest common divisor. `gcd` is never negative, so the signs stay
  where they were; then move a minus sign from the denominator to the numerator.
- Buses meet again at the **least** common multiple. The product is *a* common multiple but often
  not the first one (4 and 6: product 24, lcm 12). `math.lcm` takes any number of arguments (3.9+).
- `isqrt(n)` is the exact integer square root (the largest `r` with `r * r <= n`), so `r * r == n`
  is an exact test for any size.

## Code

```python
import math


def handshakes(n: int) -> int:
    return math.comb(n, 2)


def podium_orders(n: int, k: int = 3) -> int:
    return math.perm(n, k)


def simplify(num: int, den: int) -> tuple[int, int]:
    if den == 0:
        raise ZeroDivisionError("the denominator is 0")
    g = math.gcd(num, den)
    num, den = num // g, den // g
    if den < 0:
        num, den = -num, -den
    return num, den


def first_common_time(intervals: list[int]) -> int:
    if not intervals or any(i <= 0 for i in intervals):
        raise ValueError("intervals must be positive and not empty")
    return math.lcm(*intervals)


def is_perfect_square(n: int) -> bool:
    if n < 0:
        return False
    r = math.isqrt(n)
    return r * r == n
```

## Complexity

`gcd` and `lcm` use Euclid's algorithm: O(log n) steps for numbers of normal size. `comb` and
`perm` are O(k) multiplications. `isqrt` is O(log n) steps.

## Another way

`fractions.Fraction(num, den)` simplifies and normalises the sign by itself:
`Fraction(3, -9)` is `Fraction(-1, 3)`, and its `numerator` and `denominator` give the tuple.
Before Python 3.9 people wrote `lcm(a, b) = a * b // gcd(a, b)` and folded it over the list.
