## Walkthrough

| pair | Euclid steps | gcd | lcm | gcd*lcm == a*b |
|---|---|---|---|---|
| 12 18 | (12,18) -> (18,12) -> (12,6) -> (6,0) | 6 | 12 // 6 * 18 = 36 | 216 == 216 True |
| 7 13 | (7,13) -> (13,7) -> (7,6) -> (6,1) -> (1,0) | 1 | 91 | True |
| 0 5 | (0,5) -> (5,0) | 5 | 0 // 5 * 5 = 0 | 0 == 0 True |
| 9 9 | (9,9) -> (9,0) | 9 | 9 | True |
| 100 75 | (100,75) -> (75,25) -> (25,0) | 25 | 100 // 25 * 75 = 300 | True |
| 1 1000 | (1,1000) -> (1000,1) -> (1,0) | 1 | 1000 | True |
| 0 0 | loop does not run | 0 | 0 (guard) | 0 == 0 True |
| 5 0 | loop does not run | 5 | 5 // 5 * 0 = 0 | True |
| 8 12 | (8,12) -> (12,8) -> (8,4) -> (4,0) | 4 | 24 | True |

## Output

```
12 18 6 36 True
7 13 1 91 True
0 5 5 0 True
9 9 9 9 True
100 75 25 300 True
1 1000 1 1000 True
0 0 0 0 True
5 0 5 0 True
8 12 4 24 True
```

## Key ideas

- If `a < b`, the first pass of Euclid swaps them. That is why `(1, 1000)` and `(0, 5)` need one extra pass.
- `gcd(a, 0) = a`, so `gcd(0, 0) = 0` is the only case where the gcd is 0. That is the one case `lcm` must guard.
- The identity `gcd * lcm == a * b` holds for all non-negative pairs, including zeros.
