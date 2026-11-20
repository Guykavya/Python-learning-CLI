## Approach

Chapter section 11. Let `d` be the difference array of all additions so far (`a[i] = original[i] + d[0] + ... + d[i]`). Then the added part of the first `p` elements is

```text
sum over i < p of (d[0] + ... + d[i])  =  sum over j < p of d[j] * (p - j)
                                       =  p * (sum of d[j])  -  (sum of j * d[j])
```

`d[j]` is counted once for every `i` from `j` to `p - 1`: `p - j` times. Two Fenwick trees keep the two sums: `b1` over `d[j]`, `b2` over `j * d[j]`.

```python
class Fenwick:
    """Point add, prefix sum. Public interface 0-indexed, half-open; 1-indexed inside."""

    def __init__(self, n):
        self.n = n
        self.t = [0] * (n + 1)

    def add(self, i, v):
        i += 1
        while i <= self.n:
            self.t[i] += v
            i += i & -i

    def prefix(self, r):
        """Sum of a[0:r]."""
        total = 0
        while r > 0:
            total += self.t[r]
            r -= r & -r
        return total


class RangeAddSum:
    """Range add, range sum with two Fenwick trees. Half-open [l, r)."""

    def __init__(self, a):
        self.n = n = len(a)
        self.base = [0] * (n + 1)                 # plain prefix sums of the original values
        for i, x in enumerate(a):
            self.base[i + 1] = self.base[i] + x
        self.b1 = Fenwick(n)                      # over d[j]
        self.b2 = Fenwick(n)                      # over j * d[j]

    def add(self, l, r, v):
        self.b1.add(l, v)
        self.b2.add(l, v * l)
        if r < self.n:
            self.b1.add(r, -v)
            self.b2.add(r, -v * r)

    def prefix(self, p):
        """Sum of a[0:p]."""
        return self.base[p] + p * self.b1.prefix(p) - self.b2.prefix(p)

    def range_sum(self, l, r):
        return self.prefix(r) - self.prefix(l)
```

Check `add(2, 6, 10)` and the prefix `p = 8`: `d[2] = 10`, `d[6] = -10`, so `8 * (10 - 10) - (2 * 10 - 6 * 10) = 40`, and `36 + 40 = 76`. Indeed four elements got `+10`.

## Complexity

`O(log n)` per operation: four Fenwick updates per add, two prefix sums per prefix. `O(n)` memory.

## Another way

The lazy segment tree of p010: more code, a larger constant, but it generalises to range assign or range minimum, which the two-Fenwick trick cannot do.
