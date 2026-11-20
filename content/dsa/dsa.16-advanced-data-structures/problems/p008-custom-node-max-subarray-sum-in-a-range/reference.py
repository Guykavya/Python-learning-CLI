NEG = float("-inf")
EMPTY = (0, NEG, NEG, NEG)          # (total, best_prefix, best_suffix, best) of an empty range


def merge(x, y):
    """Record of the range x followed by the range y."""
    return (x[0] + y[0],
            max(x[1], x[0] + y[1]),
            max(y[2], y[0] + x[2]),
            max(x[3], y[3], x[2] + y[1]))


class BestRun:
    def __init__(self, a):
        self.n = n = len(a)
        self.t = [EMPTY] * n + [(v, v, v, v) for v in a]     # leaves at n .. 2n - 1
        for i in range(n - 1, 0, -1):
            self.t[i] = merge(self.t[2 * i], self.t[2 * i + 1])

    def update(self, i, v):
        t = self.t
        i += self.n
        t[i] = (v, v, v, v)
        while i > 1:
            i //= 2
            t[i] = merge(t[2 * i], t[2 * i + 1])

    def best(self, l, r):
        t = self.t
        resl, resr = EMPTY, EMPTY
        l += self.n
        r += self.n
        while l < r:
            if l % 2 == 1:
                resl = merge(resl, t[l])          # left pieces in order
                l += 1
            if r % 2 == 1:
                r -= 1
                resr = merge(t[r], resr)          # right pieces in order
            l //= 2
            r //= 2
        return merge(resl, resr)[3]
