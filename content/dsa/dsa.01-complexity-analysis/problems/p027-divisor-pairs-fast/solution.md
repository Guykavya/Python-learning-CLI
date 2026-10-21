## Approach

Three steps of improvement:

1. **Count instead of simulate.** The inner loop runs `n // i` times, so `count = sum of n // i`. O(n).
2. **Re-read the sum as pairs.** `n // i` is the number of `m` with `i * m <= n`, so `count` is the number of grid points
   `(i, m)` under the curve `i * m = n`.
3. **Use symmetry.** Every such pair has `i <= r` or `m <= r` (with `r = floor(sqrt n)`), because two numbers above
   `sqrt(n)` multiply to more than `n`. Count pairs with `i <= r` (that is `side`), double it for `m <= r`, and remove
   the `r * r` pairs in the square counted twice (inclusion-exclusion).

Check with `n = 12`: `r = 3`, `side = 12 + 6 + 4 = 22`, answer `44 - 9 = 35`.

## Code

```python
import math

n = int(input())
r = math.isqrt(n)
side = 0
for i in range(1, r + 1):
    side += n // i
print(2 * side - r * r)
```

## Complexity

O(sqrt(n)): 10^6 steps for `n = 10^12`, about a quarter of a second here. O(1) space.

## Another way

Group equal quotients: `n // i` takes only about `2 * sqrt(n)` different values, and for a given `i` the last index with
the same quotient is `n // (n // i)`. Loop over the groups, adding `quotient * group size`, and jump `i` to the next group:

```python
i = 1
total = 0
while i <= n:
    q = n // i
    last = n // q
    total += q * (last - i + 1)
    i = last + 1
```

This "quotient blocks" technique also works for sums like `sum of i * (n // i)`, where symmetry is less obvious.

## About the square root

`int(n ** 0.5)` goes through a float. For large `n` it can be one too big or too small. `math.isqrt` is exact.
If you use the float version, correct it: `while r * r > n: r -= 1` and `while (r + 1) * (r + 1) <= n: r += 1`.
