## Approach

Turn every kind into a **few 0/1 items** and run the downward 0/1 loop of chapter section 10.

**Binary splitting.** Split `count` into bundles `1, 2, 4, ..., 2**(k-1)` while the sum stays within `count`, then one last bundle `r` with the rest. For `count = 13` that is `1, 2, 4, 6`. Two facts make it correct:

- Every number `c` from 0 to `count` is a sum of some bundles, each used once. With `1, 2, ..., 2**(k-1)` you can make every number up to `2**k - 1` (binary). Numbers above that use the last bundle `r` plus a binary number for the rest.
- No choice of bundles adds up to more than `count`, because all bundles together are exactly `count`.

So "pick some bundles, each at most once" describes exactly the choices "0 to `count` copies". A bundle of `b` copies is a 0/1 item with weight `b * weight` and value `b * value`.

```python
def bounded_knapsack(items, W):
    g = [0] * (W + 1)
    for weight, value, count in items:
        b = 1
        while count > 0:                     # bundles 1, 2, 4, ... and the rest
            take = min(b, count)
            bw, bv = take * weight, take * value
            for w in range(W, bw - 1, -1):   # each bundle is a 0/1 item: downwards
                cand = g[w - bw] + bv
                if cand > g[w]:
                    g[w] = cand
            count -= take
            b *= 2
    return g[W]
```

Check with `(1, 5, 3)` and `W = 10`: bundles of 1 and 2 copies (weights 1 and 2, values 5 and 10). Both fit: 15, which is 3 copies. A 4th copy cannot appear, because no bundle set sums to 4.

(If a bundle is heavier than `W`, `range(W, bw - 1, -1)` is empty and the bundle is ignored. That is fine: smaller bundles still cover every count that fits.)

## Complexity

`O(W * sum(log2(count + 1)))` time, `O(W)` space. For 100 kinds with 1000 copies: about 100 * 10 bundles * 5000 capacities = 5 million steps, instead of 300 million with one item per copy.

## Another way

Loop over the number of copies directly: for each kind, for `w` from `W` down to 0, try `k = 1 .. count` copies with `g[w - k * weight] + k * value`. It is correct and needs no trick, but costs `O(W * count)` per kind. The fastest known method groups capacities by `w % weight` and uses a sliding-window maximum (a monotonic deque, dsa.05) for `O(W)` per kind; binary splitting is almost as fast and much simpler.
