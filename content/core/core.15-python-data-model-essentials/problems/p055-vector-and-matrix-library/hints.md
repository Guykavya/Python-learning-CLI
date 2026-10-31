## Hint 1

Start with `Vector` and write the container methods first (`__len__`, `__iter__`, `__getitem__`): once `__iter__` works, `list(v)`, `in`, `max`, unpacking and `zip` work for free, and most arithmetic is `Vector(*(a + b for a, b in zip(self, other)))`. Which operators receive the *other* operand on the left side (`3 * v`) and what must they return when the types do not fit?

## Hint 2

Rules that save work: (1) every binary operator checks `isinstance(other, ...)` first and `return NotImplemented` if it does not know the type; (2) `__rmul__ = __mul__` is enough for scalars; (3) `sum()` needs `__radd__` handling `0`; (4) `__hash__` must use the same data as `__eq__` (hash the tuple of components, or the tuple of rows); (5) store the data as **tuples** so the objects really are immutable. For the Matrix, keep a tuple of tuples `_rows`, and let `__iter__` produce `Vector(*row)`.

## Hint 3

Matrix product by definition: entry `(i, j)` of `A @ B` is `sum(a * b for a, b in zip(A_row_i, B_col_j))`; the columns of `B` are `zip(*B._rows)`.

```
__matmul__(self, other):
    Matrix: check self.cols == other.rows (else ValueError); return Matrix([[row . col for col in cols] for row in rows])
    Vector: check self.cols == len(other); return Vector(*(row . other for row in rows))
    else:   return NotImplemented
__rmatmul__(self, other):   # other @ self where other is a Vector
    Vector: check len(other) == self.rows; return Vector(*(other . col for col in columns))
__pow__(self, n): result = identity ; while n: if n & 1: result = result @ base ; base = base @ base ; n >>= 1
```
