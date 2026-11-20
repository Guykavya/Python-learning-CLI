## Approach

Chapter section 1. `pre[k]` is the sum of the first `k` elements; a range sum is one subtraction, `pre[r] - pre[l]`.

An update is the weak spot: `a[i]` is part of **every** prefix longer than `i`, so `pre[i + 1]` to `pre[n]` all change by the same `delta`.

```python
class PrefixSums:
    def __init__(self, a):
        self.a = list(a)
        self.n = len(a)
        self.pre = [0] * (self.n + 1)
        for i, x in enumerate(a):
            self.pre[i + 1] = self.pre[i] + x

    def query(self, l, r):
        return self.pre[r] - self.pre[l]

    def set(self, i, v):
        delta = v - self.a[i]
        self.a[i] = v
        pre = self.pre
        for k in range(i + 1, self.n + 1):      # every prefix longer than i contains a[i]
            pre[k] += delta
        return self.n - i
```

## Complexity

| | Time |
|---|---|
| build | `O(n)` |
| `query` | `O(1)` |
| `set` | `O(n - i)`, `O(n)` in the worst case |

With random positions an update repairs `n / 2` entries on average. For 5 * 10**4 updates on `n = 10**5` that is about 2.5 * 10**9 additions; a segment tree or a Fenwick tree needs about 17 steps per update. That is why the rest of the module exists.

## Another way

Rebuild `pre` from scratch after each update with `itertools.accumulate` (fast C code, but still `O(n)`), or keep updates in a small list and add their effect to each query (`O(number of pending updates)` per query), rebuilding once in a while: a first taste of square-root decomposition (p026).
