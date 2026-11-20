import math


class BlockSum:
    def __init__(self, a):
        self.a = list(a)
        self.n = len(a)
        self.B = max(1, math.isqrt(self.n))
        self.blocks = []

    def update(self, i, v):
        self.a[i] = v

    def query(self, l, r):
        """(sum of a[l:r], number of steps)"""
        return sum(self.a[l:r]), r - l
