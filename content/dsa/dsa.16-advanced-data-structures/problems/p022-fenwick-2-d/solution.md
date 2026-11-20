## Approach

Chapter section 14. Nest the 1-D Fenwick loops: an update climbs the rows, and for every row cell climbs the columns; a prefix query descends both. A rectangle is four prefix rectangles combined by inclusion-exclusion.

```python
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
```

`P(r2, c2)` counts the whole corner rectangle; subtracting `P(r1, c2)` (the rows above) and `P(r2, c1)` (the columns to the left) removes the top-left corner `P(r1, c1)` twice, so it is added back once.

## Complexity

`O(log R * log C)` per update, four times that per rectangle, `O(R * C)` memory. A 300 x 300 grid is 90,000 cells; 3000 x 3000 would be about 70 MB of Python lists, the practical limit (chapter section 19).

## Another way

A 2-D prefix-sum table (dsa.03) answers rectangles in `O(1)` but an update costs `O(R * C)`. If all updates come before all questions, build the table once at the end. A Fenwick tree of rows where each row is its own 1-D Fenwick tree is the same structure as this one.
