class Fenwick2D:
    """Point add, rectangle sum. 0-indexed, half-open rectangles; 1-indexed inside."""

    def __init__(self, rows, cols):
        self.R, self.C = rows, cols
        self.t = [[0] * (cols + 1) for _ in range(rows + 1)]

    def add(self, r, c, v):
        i = r + 1
        while i <= self.R:
            row = self.t[i]
            j = c + 1
            while j <= self.C:
                row[j] += v
                j += j & -j
            i += i & -i

    def prefix(self, r, c):
        """Sum of rows [0, r) and columns [0, c)."""
        total = 0
        i = r
        while i > 0:
            row = self.t[i]
            j = c
            while j > 0:
                total += row[j]
                j -= j & -j
            i -= i & -i
        return total

    def rect(self, r1, c1, r2, c2):
        """Sum of rows [r1, r2) and columns [c1, c2): inclusion-exclusion on four prefixes."""
        return (self.prefix(r2, c2) - self.prefix(r1, c2)
                - self.prefix(r2, c1) + self.prefix(r1, c1))
