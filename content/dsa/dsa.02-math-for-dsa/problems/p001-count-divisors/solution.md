## Approach

`d` divides `n` exactly when the remainder `n % d` is 0. Every divisor is between 1 and `n`, so we test all of
those numbers and count the hits.

## Code

```python
q = int(input())
for _ in range(q):
    n = int(input())
    count = 0
    for d in range(1, n + 1):
        if n % d == 0:
            count += 1
    print(count)
```

## Complexity

O(n) per query. With `n <= 100000` and `q <= 10` that is at most a million remainders: fast enough.
For `n = 10^9` this would take minutes, which is why the next problems look for something faster.

## Another way

Divisors come in pairs `(d, n // d)`. Loop `d` only up to the square root of `n`, add 2 for each hit, and add
only 1 when `d * d == n` (a perfect square, where the pair is the same number twice). That is O(sqrt n).
