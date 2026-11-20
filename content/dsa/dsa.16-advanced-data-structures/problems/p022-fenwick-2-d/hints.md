## Hint 1

`t[i][j]` (1-indexed) covers `lowbit(i)` rows ending at `i` and `lowbit(j)` columns ending at `j`. An update runs the 1-D update loop over `i`, and inside it the 1-D update loop over `j`. A prefix query runs the two prefix loops the same way.

## Hint 2

Inclusion-exclusion, as for 2-D prefix sums (dsa.03): `rect(r1, c1, r2, c2) = P(r2, c2) - P(r1, c2) - P(r2, c1) + P(r1, c1)`, where `P(r, c)` is the sum of rows `[0, r)` and columns `[0, c)`.

## Hint 3

```
add(r, c, v):   i = r + 1; while i <= R: j = c + 1; while j <= C: t[i][j] += v; j += j & -j; ... i += i & -i
prefix(r, c):   i = r; while i > 0: j = c; while j > 0: total += t[i][j]; j -= j & -j; ... i -= i & -i
```
