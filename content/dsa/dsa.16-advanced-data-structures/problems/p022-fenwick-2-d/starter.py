class Fenwick2D:
    """Point add, rectangle sum. Half-open rectangles."""

    def __init__(self, rows, cols):
        self.g = [[0] * cols for _ in range(rows)]

    def add(self, r, c, v):
        self.g[r][c] += v

    def rect(self, r1, c1, r2, c2):
        return sum(sum(row[c1:c2]) for row in self.g[r1:r2])      # O(rows * cols)
