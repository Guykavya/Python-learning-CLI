class Fenwick:
    """Point add, prefix sum. Public interface 0-indexed, half-open; 1-indexed inside."""

    def __init__(self, n):
        self.n = n
        self.t = [0] * (n + 1)

    def add(self, i, v):
        i += 1
        while i <= self.n:
            self.t[i] += v
            i += i & -i

    def prefix(self, r):
        """Sum of a[0:r]."""
        total = 0
        while r > 0:
            total += self.t[r]
            r -= r & -r
        return total


def smaller_after(nums):
    ranks = {v: i for i, v in enumerate(sorted(set(nums)))}
    bit = Fenwick(len(ranks))
    out = [0] * len(nums)
    for i in range(len(nums) - 1, -1, -1):        # from the right: the tree holds the later numbers
        k = ranks[nums[i]]
        out[i] = bit.prefix(k)                    # later numbers with a strictly smaller rank
        bit.add(k, 1)
    return out
