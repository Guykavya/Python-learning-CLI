## Approach

Chapter section 6. Leaves sit at `t[n .. 2n - 1]`; node `i` has the children `2i` and `2i + 1`. The query climbs from both ends of `[l + n, r + n)` at once. A node is taken exactly when its parent would stick out of the range: an odd `l` (a right child) or an odd `r` (so `r - 1` is a left child).

The order matters for non-commutative combines. Everything the **left** pointer takes lies to the left of everything it takes later; everything the **right** pointer takes lies to the right of everything it takes later. So the left pieces are appended at the end of `resl`, the right pieces are put at the front of `resr`, and the answer is `resl` followed by `resr`.

```python
class IterSeg:
    """Bottom-up segment tree, size 2n, any associative combine. Half-open [l, r)."""

    def __init__(self, a, combine, identity):
        self.n = n = len(a)
        self.f = combine
        self.e = identity
        self.t = [identity] * n + list(a)        # t[n + i] = a[i]
        for i in range(n - 1, 0, -1):
            self.t[i] = combine(self.t[2 * i], self.t[2 * i + 1])

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
            if l % 2 == 1:                       # l is a right child: take it, move right
                resl = f(resl, t[l])
                l += 1
            if r % 2 == 1:                       # r - 1 is a left child inside the range
                r -= 1
                resr = f(t[r], resr)
            l //= 2
            r //= 2
        return f(resl, resr)                     # left pieces, then right pieces
```

The starter has only one accumulator and appends the right pieces at the end: for sums that is fine (`+` is commutative), for strings it scrambles the order.

For `n` not a power of two, some internal nodes (for example node 1 when `n = 5`) join pieces that are not neighbours in the array. The query never takes them: it only takes a node when both of its pointers have not crossed, and that only happens for nodes whose leaves lie inside `[l, r)`.

## Complexity

`O(n)` build, `O(log n)` per update and query, exactly `2n` memory. No function calls per node, so it is several times faster than the recursive tree in Python (chapter section 19).

## Another way

Make the size a power of two (`size >= n`, pad with the identity). Then the tree is a perfect binary tree, every node is a contiguous range, and descents ("find the first position where ...") become easy (chapter section 7, the k-th zero).
