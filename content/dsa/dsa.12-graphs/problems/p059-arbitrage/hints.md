## Hint 1

A cycle is profitable when `r1 * r2 * ... * rk > 1`. Take the logarithm of both sides: `log r1 + ... + log rk > 0`. Multiply by -1: `(-log r1) + ... + (-log rk) < 0`. So with edge weights `w = -log(r)`, which kind of cycle are you looking for, and which algorithm finds it?

## Hint 2

Start with `dist = [0.0] * n` (every currency is a start), run `n` rounds of "relax every edge", and stop early if a round changes nothing. Make "changes" robust against rounding: only relax when `dist[u] + w < dist[v] - 1e-12`. If the last round (round `n`) still changes something, there is a negative cycle.

## Hint 3

```
dist = [0.0] * n
for rnd in range(n):
    changed = False
    for a, b, r in rates:
        w = -log(r)
        if dist[a] + w < dist[b] - EPS:
            dist[b] = dist[a] + w;  changed = True
    if not changed: return False
return True               # still changing after n rounds
```
