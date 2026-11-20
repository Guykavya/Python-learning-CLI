## Approach

Three structures, one convention, one harness. Each class is the version from earlier in this module: the `O(n)`-built Fenwick tree (p014), the iterative segment tree with ordered accumulators (p006), and the sparse table with a `log` table (p023).

```python
class FenwickTree:
    """Point add, prefix and range sums. 0-indexed, half-open; 1-indexed inside."""

    def __init__(self, n_or_list):
        if isinstance(n_or_list, int):
            self.n = n_or_list
            self.t = [0] * (self.n + 1)
        else:
            a = list(n_or_list)
            self.n = n = len(a)
            self.t = [0] + a                       # t[k] = a[k - 1], then push each cell into its parent
            for k in range(1, n + 1):
                parent = k + (k & -k)
                if parent <= n:
                    self.t[parent] += self.t[k]

    def add(self, i, v):
        i += 1
        while i <= self.n:
            self.t[i] += v
            i += i & -i

    def prefix(self, r):
        total = 0
        while r > 0:
            total += self.t[r]
            r -= r & -r
        return total

    def range_sum(self, l, r):
        return self.prefix(r) - self.prefix(l)


class SegmentTree:
    """Iterative segment tree, size 2n, any associative merge (order kept). 0-indexed, half-open."""

    def __init__(self, a, merge, identity):
        self.n = n = len(a)
        self.f = merge
        self.e = identity
        self.t = [identity] * n + list(a)
        for i in range(n - 1, 0, -1):
            self.t[i] = merge(self.t[2 * i], self.t[2 * i + 1])

    def update(self, i, v):
        t, f = self.t, self.f
        i += self.n
        t[i] = v
        while i > 1:
            i //= 2
            t[i] = f(t[2 * i], t[2 * i + 1])

    def query(self, l, r):
        t, f = self.t, self.f
        resl, resr = self.e, self.e
        l += self.n
        r += self.n
        while l < r:
            if l % 2 == 1:
                resl = f(resl, t[l])
                l += 1
            if r % 2 == 1:
                r -= 1
                resr = f(t[r], resr)
            l //= 2
            r //= 2
        return f(resl, resr)


class SparseTable:
    """Static array, idempotent f, O(1) query on [l, r) with l < r."""

    def __init__(self, a, f):
        n = len(a)
        self.f = f
        self.lg = [0] * (n + 1)
        for i in range(2, n + 1):
            self.lg[i] = self.lg[i // 2] + 1
        self.table = [list(a)]
        k = 1
        while (1 << k) <= n:
            prev, half = self.table[-1], 1 << (k - 1)
            self.table.append([f(prev[i], prev[i + half]) for i in range(n - (1 << k) + 1)])
            k += 1

    def query(self, l, r):
        k = self.lg[r - l]
        row = self.table[k]
        return self.f(row[l], row[r - (1 << k)])
```

The shared harness in the tests takes a structure, a way to apply an update to it and to a plain list, and a way to ask a question of both; it runs random operations and stops at the first difference with a message that names the structure and the step. Using **one** harness for every structure catches the classic slips: a closed range in one class and half-open in another, a wrong identity, a non-commutative merge taken in the wrong order, and a build that differs from repeated updates.

## Complexity

| | Build | Update | Query | Memory |
|---|---|---|---|---|
| `FenwickTree` | `O(n)` | `O(log n)` | `O(log n)` | `n + 1` |
| `SegmentTree` | `O(n)` | `O(log n)` | `O(log n)` | `2n` |
| `SparseTable` | `O(n log n)` | none | `O(1)` | `O(n log n)` |

## Another way

Add a lazy segment tree (p010/p011) with pluggable `apply` and `compose` functions to cover range updates too: the "recipe for any lazy tree" of chapter section 9 turned into a class.
