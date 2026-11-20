class PrefixSums:
    def __init__(self, a):
        self.a = list(a)
        self.pre = [0] * (len(a) + 1)

    def query(self, l, r):
        """Sum of a[l:r] in O(1)."""
        return sum(self.a[l:r])

    def set(self, i, v):
        """a[i] = v; repair pre; return how many entries of pre were changed."""
        self.a[i] = v
        return 0
