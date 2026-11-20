## Hint 1

`prefix(p) = sum over i < p of (d[0] + ... + d[i]) = sum over j < p of d[j] * (p - j) = p * sum(d[j]) - sum(j * d[j])`, both sums over `j < p`.

## Hint 2

Keep `b1` over `d[j]` and `b2` over `j * d[j]`. A range add of `v` on `[l, r)` is `d[l] += v`, `d[r] -= v`, so: `b1.add(l, v)`, `b1.add(r, -v)`, `b2.add(l, v * l)`, `b2.add(r, -v * r)` (skip the `r` updates when `r == n`).

## Hint 3

```
prefix(p) = base[p] + p * b1.prefix(p) - b2.prefix(p)       # base = plain prefix sums of a
range_sum(l, r) = prefix(r) - prefix(l)
```
