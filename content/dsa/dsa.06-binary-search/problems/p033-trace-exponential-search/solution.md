## Approach

Run the doubling loop first, then the binary search on `[bound // 2, bound]`.

## Expected output

```text
double: f( 1 ) = 1
double: f( 2 ) = 4
double: f( 4 ) = 16
double: f( 8 ) = 64
double: f( 16 ) = 256
bound 32
lo 16 hi 32 mid 24 f(mid) 576 ok True
lo 16 hi 24 mid 20 f(mid) 400 ok False
lo 21 hi 24 mid 22 f(mid) 484 ok False
lo 23 hi 24 mid 23 f(mid) 529 ok True
answer 23
```

## Why

Doubling: `bound = 1, 2, 4, 8, 16` all have `f < 500` (1, 4, 16, 64, 256), so each prints a line; `f(32) = 1024 >= 500` stops it. That was 6 evaluations.
Then `lo = 16, hi = 32`: `mid = 24` (576, True) gives `hi = 24`; `mid = 20` (400, False) gives `lo = 21`; `mid = 22` (484, False) gives `lo = 23`; `mid = 23` (529, True) gives `hi = 23`. Answer 23 after 4 more evaluations: 10 in total, against 23 for a linear scan.
The second phase may start at `bound // 2` because the last doubling step showed `f(bound // 2) < target`, so the answer is above it. For 5 * 10^17 the square root is about 7 * 10^8, so about 30 doublings.
