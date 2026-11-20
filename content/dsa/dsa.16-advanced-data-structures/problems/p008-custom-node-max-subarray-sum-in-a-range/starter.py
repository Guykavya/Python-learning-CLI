class BestRun:
    """Maximum non-empty subarray sum on a[l:r], with point updates."""

    def __init__(self, a):
        self.a = list(a)

    def update(self, i, v):
        self.a[i] = v

    def best(self, l, r):
        best = cur = self.a[l]                # Kadane over the range: O(r - l)
        for x in self.a[l + 1:r]:
            cur = max(x, cur + x)
            best = max(best, cur)
        return best
