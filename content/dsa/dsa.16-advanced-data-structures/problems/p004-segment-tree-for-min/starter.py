class MinTree:
    """Range minimum, point update. Half-open [l, r)."""

    def __init__(self, a):
        self.a = list(a)

    def update(self, i, v):
        self.a[i] = v

    def query(self, l, r):
        return min(self.a[l:r], default=0)
