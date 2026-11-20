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
