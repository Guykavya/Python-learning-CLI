import math


class BlockSum:
    def __init__(self, a):
        self.a = list(a)
        self.n = len(a)
        self.B = max(1, math.isqrt(self.n))
        nb = (self.n + self.B - 1) // self.B
        self.blocks = [sum(self.a[b * self.B:(b + 1) * self.B]) for b in range(nb)]

    def update(self, i, v):
        self.blocks[i // self.B] += v - self.a[i]
        self.a[i] = v

    def query(self, l, r):
        a, blocks, B = self.a, self.blocks, self.B
        total = touched = 0
        while l < r and l % B != 0:           # left partial block, one by one
            total += a[l]
            l += 1
            touched += 1
        while l + B <= r:                     # whole blocks
            total += blocks[l // B]
            l += B
            touched += 1
        while l < r:                          # right partial block
            total += a[l]
            l += 1
            touched += 1
        return total, touched
