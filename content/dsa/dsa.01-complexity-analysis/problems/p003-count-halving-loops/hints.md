## Hint 1

Trace `n = 10` fully. Halving: 10, 5, 2, 1. How many divisions was that? Doubling: 1, 2, 4, 8, 16. How many
multiplications until `p` is no longer less than 10?

## Hint 2

The halving counter is the largest `k` with `2^k <= n` (the "floor" of `log2 n`). The doubling counter is the
smallest `k` with `2^k >= n` (the "ceiling" of `log2 n`). For `n = 1` both loops do not run at all.

## Hint 3

For 1000: `2^9 = 512 <= 1000 < 1024 = 2^10`. For 1000000: `2^19 = 524288 <= 1000000 < 1048576 = 2^20`.
