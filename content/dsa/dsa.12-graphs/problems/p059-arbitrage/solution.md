## Approach

The log turns the product of a cycle into a sum, and the minus sign turns "product greater than 1" into "sum less than 0": arbitrage is exactly a negative cycle for the weights `-log(r)`. Because profit can hide in any part of the market, every currency starts at distance 0 (a virtual source with 0-edges to all). Without a negative cycle, the distances settle in at most `n` rounds (the virtual source makes `n + 1` vertices); if round `n` still improves something, a negative cycle exists. The tolerance `EPS` ignores improvements that are pure rounding noise: a cycle of true product 1 has a log-sum of about `1e-16`, while a real profit of 0.1 % gives about `-1e-3`.

## Code

```python
import math


def has_arbitrage(n, rates):
    EPS = 1e-12
    edges = [(a, b, -math.log(r)) for a, b, r in rates]
    dist = [0.0] * n
    for _ in range(n):
        changed = False
        for a, b, w in edges:
            if dist[a] + w < dist[b] - EPS:
                dist[b] = dist[a] + w
                changed = True
        if not changed:
            return False
    return True
```

## Complexity

`O(n * E)` time, `O(n + E)` memory.

## Another way

Work with products directly: keep `best[c]`, the most units of currency `c` reachable from one unit of "anything", start with `best = [1.0] * n`, and relax `best[a] * r > best[b] * (1 + 1e-12)`. The same rounds, no logarithms. Or run Floyd-Warshall on products (maximise instead of minimise) and look for `prod[i][i] > 1 + 1e-9` on the diagonal: `O(n^3)`. It needs the tolerance in the update too (`p[i][k] * p[k][j] > p[i][j] * (1 + 1e-12)`): without it, cycles whose product is `1.0000000000000002` by rounding are multiplied into each other again and again, and a consistent market of 60 currencies ends with `inf` on the diagonal (measured).
