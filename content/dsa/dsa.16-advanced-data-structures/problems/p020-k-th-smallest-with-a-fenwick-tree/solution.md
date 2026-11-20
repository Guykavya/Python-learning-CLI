## Approach

Chapter section 13. A Fenwick tree of counts per value answers "how many items are `<= v`" as a prefix sum, and the `k`-th smallest is the first `v` where that reaches `k`. Instead of a binary search with a `prefix` call per step (`O(log**2 m)`), walk the bits from high to low: `pos` always has its lower bits zero, so `t[pos + pw]` covers exactly the next block `pos + 1 .. pos + pw`, and one look decides whether to skip it.

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


class MinuteBag:
    """Multiset of values 0..m-1 with k-th smallest, by binary descent on a Fenwick tree of counts."""

    def __init__(self, m):
        self.m = m
        self.bit = Fenwick(m)
        self.count = [0] * m
        self.total = 0

    def insert(self, v):
        self.bit.add(v, 1)
        self.count[v] += 1
        self.total += 1

    def remove(self, v):
        if self.count[v] == 0:
            return False
        self.bit.add(v, -1)
        self.count[v] -= 1
        self.total -= 1
        return True

    def size(self):
        return self.total

    def kth(self, k):
        if k < 1 or k > self.total:
            return -1
        t, m = self.bit.t, self.m
        pos = 0
        pw = 1 << (m.bit_length() - 1)          # the largest power of two <= m
        while pw:
            nxt = pos + pw
            if nxt <= m and t[nxt] < k:         # the block pos+1 .. nxt has fewer than k items: skip it
                pos = nxt
                k -= t[nxt]
            pw >>= 1
        return pos                              # 1-indexed pos + 1 is the answer; 0-indexed that is pos
```

When the loop ends, `pos` is the largest (1-indexed) position whose prefix count is still `< k`, so the `k`-th item sits at 1-indexed `pos + 1`, which is the 0-indexed value `pos`.

## Complexity

`O(log m)` for every operation, `O(m)` memory.

## Another way

A sorted list with `bisect.insort` and `list.remove` (the starter's idea, made correct): `kth` is a plain index, but insertions and removals shift the list, `O(n)` each in theory (fast in C for moderate sizes). A segment tree with the descent of chapter section 7 (the k-th zero) works too, with more code.
