## Walkthrough

| n | halving sequence | halvings | doubling sequence | doublings |
|---|---|---|---|---|
| 1 | 1 (loop never runs) | 0 | 1 (loop never runs) | 0 |
| 2 | 2, 1 | 1 | 1, 2 | 1 |
| 10 | 10, 5, 2, 1 | 3 | 1, 2, 4, 8, 16 | 4 |
| 64 | 64, 32, 16, 8, 4, 2, 1 | 6 | 1, 2, ..., 64 | 6 |
| 1000 | 1000, 500, 250, 125, 62, 31, 15, 7, 3, 1 | 9 | 1, 2, ..., 512, 1024 | 10 |
| 1000000 | ... | 19 | ... up to 2^20 | 20 |

Output:

```
1 0 0
2 1 1
10 3 4
64 6 6
1000 9 10
1000000 19 20
```

## Key idea

Halving `n` until it reaches 1 takes about `log2(n)` steps; so does doubling 1 until it reaches `n`.
The halving loop gives `floor(log2 n)`, the doubling loop gives `ceil(log2 n)`. They agree exactly when
`n` is a power of two (1, 2, 64 here).

The striking part is how slowly this grows. Going from `n = 1000` to `n = 1000000` (a thousand times more)
adds only 10 steps. A loop that halves is O(log n), and O(log n) is almost free even for `n = 10^18`
(about 60 steps).
