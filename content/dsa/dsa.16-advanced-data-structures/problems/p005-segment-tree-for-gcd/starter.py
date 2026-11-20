import math


class GcdTree:
    """Range gcd, point update. Half-open [l, r)."""

    def __init__(self, a):
        self.a = list(a)

    def update(self, i, v):
        self.a[i] = v

    def query(self, l, r):
        return math.gcd(*self.a[l:r]) if r - l > 1 else 0
