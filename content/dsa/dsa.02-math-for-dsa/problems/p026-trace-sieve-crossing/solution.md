## Walkthrough

- `p = 2`: walk 4, 6, ..., 50 (24 numbers, all new).
- `p = 3`: walk 9, 12, 15, ..., 48. Even ones are already crossed, so the new ones are 9, 15, 21, 27, 33, 39, 45.
- `p = 4`: `4 * 4 = 16 <= 50`, but `is_prime[4]` is `False`, so nothing is printed.
- `p = 5`: walk 25, 30, 35, 40, 45, 50. 30, 40, 50 are even, 45 is a multiple of 3. New: 25 and 35.
- `p = 6`: crossed, skipped.
- `p = 7`: walk 49, 56 > 50. New: 49.
- `p = 8`: `64 > 50`, `break`.

## Output

```
2 [4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36, 38, 40, 42, 44, 46, 48, 50]
3 [9, 15, 21, 27, 33, 39, 45]
5 [25, 35]
7 [49]
primes 15
last 47
```

The primes up to 50 are 2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47: fifteen primes, the largest 47.

## Key ideas

- A composite `m <= n` has a prime factor `p` with `p * p <= m`. So after crossing off with all primes up to `sqrt(n)`,
  only primes remain.
- Starting at `p * p` is safe, because `p * k` with `k < p` has a smaller prime factor and was crossed earlier.
- Total work is about `n log log n`: much less than testing each number by trial division.
