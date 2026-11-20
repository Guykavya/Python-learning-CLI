class SparseMin:
    """Static range minimum with O(1) queries. Half-open [l, r), l < r."""

    def __init__(self, a):
        n = len(a)
        self.lg = [0] * (n + 1)                   # lg[L] = floor(log2(L))
        for i in range(2, n + 1):
            self.lg[i] = self.lg[i // 2] + 1
        self.table = [list(a)]
        k = 1
        while (1 << k) <= n:
            prev, half = self.table[-1], 1 << (k - 1)
            self.table.append([min(prev[i], prev[i + half]) for i in range(n - (1 << k) + 1)])
            k += 1

    def query(self, l, r):
        k = self.lg[r - l]
        row = self.table[k]
        return min(row[l], row[r - (1 << k)])     # two blocks of 2**k that cover [l, r), maybe overlapping
