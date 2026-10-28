## Approach

**Layout.** The data lives in one tuple (`_c` for vectors, `_rows` for matrices). That makes the objects immutable, easy to compare and hash, and each operator simply builds a **new** object from the tuples.

**Protocols first.** `__len__`, `__iter__` and `__getitem__` give a Vector `list()`, `in`, `max`, unpacking and `zip`. For a Matrix, iterating yields rows as Vectors, so `sum(row)`, `abs(row)` and `zip(*m)` work. `__repr__` follows the "can be pasted back" convention, so `eval(repr(x)) == x`. `__format__` applies the spec to each component.

**Equality and hashing.** `__eq__` compares the stored tuples; `__hash__` hashes the same tuples, so the rule "equal objects have equal hashes" holds. Both return/propagate `NotImplemented` for foreign types.

**Operators.** Each binary method first checks the type of the right operand and returns `NotImplemented` if it is not one it understands. Then it checks sizes (`ValueError`) and builds the result. Scalar multiplication is symmetric, so `__rmul__ = __mul__`. `__radd__` exists only for `sum()`: `sum` computes `0 + v`, and `int.__add__` returns `NotImplemented`, so Python calls `v.__radd__(0)`.

**Products.** `Vector @ Vector` is the dot product. `Matrix @ Matrix` takes the rows of the left side and the columns (`zip(*rows)`) of the right side. `Matrix @ Vector` is the rows against the vector. `Vector @ Matrix` goes through `Matrix.__rmatmul__`, because `Vector.__matmul__` returns `NotImplemented` for a Matrix. `__pow__` squares the base and multiplies into the result for each set bit of `n`, so `m ** 30` needs about 5 squarings.

## Code

```python
import math

NUMBER = (int, float)


class Vector:
    def __init__(self, *components):
        if not components:
            raise ValueError("a Vector needs at least one component")
        for c in components:
            if not isinstance(c, NUMBER):
                raise TypeError(f"components must be numbers, got {c!r}")
        self._c = tuple(components)

    @classmethod
    def zeros(cls, n):
        if n < 1:
            raise ValueError("n must be at least 1")
        return cls(*([0] * n))

    # ---- container protocol
    def __len__(self):
        return len(self._c)

    def __iter__(self):
        return iter(self._c)

    def __getitem__(self, index):
        if isinstance(index, slice):
            return Vector(*self._c[index])
        return self._c[index]

    # ---- text
    def __repr__(self):
        return "Vector(" + ", ".join(repr(c) for c in self._c) + ")"

    def __format__(self, spec):
        return "(" + ", ".join(format(c, spec) for c in self._c) + ")"

    def __str__(self):
        return format(self, "")

    # ---- equality and hashing
    def __eq__(self, other):
        if not isinstance(other, Vector):
            return NotImplemented
        return self._c == other._c

    def __hash__(self):
        return hash(self._c)

    # ---- truth, abs, neg
    def __bool__(self):
        return any(c != 0 for c in self._c)

    def __abs__(self):
        return math.sqrt(sum(c * c for c in self._c))

    def __neg__(self):
        return Vector(*(-c for c in self._c))

    # ---- arithmetic
    def _check_same_size(self, other):
        if len(self) != len(other):
            raise ValueError(f"vectors have different sizes: {len(self)} and {len(other)}")

    def __add__(self, other):
        if not isinstance(other, Vector):
            return NotImplemented
        self._check_same_size(other)
        return Vector(*(a + b for a, b in zip(self._c, other._c)))

    def __radd__(self, other):
        if isinstance(other, int) and other == 0:       # lets sum([v1, v2]) work
            return self
        return NotImplemented

    def __sub__(self, other):
        if not isinstance(other, Vector):
            return NotImplemented
        self._check_same_size(other)
        return Vector(*(a - b for a, b in zip(self._c, other._c)))

    def __mul__(self, k):
        if not isinstance(k, NUMBER):
            return NotImplemented
        return Vector(*(c * k for c in self._c))

    __rmul__ = __mul__

    def __truediv__(self, k):
        if not isinstance(k, NUMBER):
            return NotImplemented
        return Vector(*(c / k for c in self._c))

    def __matmul__(self, other):
        if not isinstance(other, Vector):
            return NotImplemented
        self._check_same_size(other)
        return sum(a * b for a, b in zip(self._c, other._c))


class Matrix:
    def __init__(self, rows):
        rows = [tuple(row) for row in rows]
        if not rows or not rows[0]:
            raise ValueError("a Matrix needs at least one row and one column")
        if any(len(row) != len(rows[0]) for row in rows):
            raise ValueError("all rows must have the same length")
        for row in rows:
            for x in row:
                if not isinstance(x, NUMBER):
                    raise TypeError(f"entries must be numbers, got {x!r}")
        self._rows = tuple(rows)

    @classmethod
    def identity(cls, n):
        if n < 1:
            raise ValueError("n must be at least 1")
        return cls([[1 if i == j else 0 for j in range(n)] for i in range(n)])

    @property
    def shape(self):
        return (len(self._rows), len(self._rows[0]))

    # ---- container protocol
    def __len__(self):
        return len(self._rows)

    def __iter__(self):
        for row in self._rows:
            yield Vector(*row)

    def __getitem__(self, key):
        if isinstance(key, tuple):
            if len(key) != 2:
                raise TypeError("use m[i] or m[i, j]")
            i, j = key
            return self._rows[i][j]
        if isinstance(key, slice):
            raise TypeError("Matrix does not support slices")
        return Vector(*self._rows[key])

    # ---- text, equality, hash
    def __repr__(self):
        return f"Matrix({[list(row) for row in self._rows]!r})"

    def __str__(self):
        return "\n".join(" ".join(str(x) for x in row) for row in self._rows)

    def __eq__(self, other):
        if not isinstance(other, Matrix):
            return NotImplemented
        return self._rows == other._rows

    def __hash__(self):
        return hash(self._rows)

    # ---- transpose
    def transpose(self):
        return Matrix(zip(*self._rows))

    @property
    def T(self):
        return self.transpose()

    # ---- arithmetic
    def _check_same_shape(self, other):
        if self.shape != other.shape:
            raise ValueError(f"shapes differ: {self.shape} and {other.shape}")

    def __neg__(self):
        return Matrix([[-x for x in row] for row in self._rows])

    def __add__(self, other):
        if not isinstance(other, Matrix):
            return NotImplemented
        self._check_same_shape(other)
        return Matrix([[a + b for a, b in zip(r1, r2)] for r1, r2 in zip(self._rows, other._rows)])

    def __sub__(self, other):
        if not isinstance(other, Matrix):
            return NotImplemented
        self._check_same_shape(other)
        return Matrix([[a - b for a, b in zip(r1, r2)] for r1, r2 in zip(self._rows, other._rows)])

    def __mul__(self, k):
        if not isinstance(k, NUMBER):
            return NotImplemented
        return Matrix([[x * k for x in row] for row in self._rows])

    __rmul__ = __mul__

    def __matmul__(self, other):
        if isinstance(other, Matrix):
            if self.shape[1] != other.shape[0]:
                raise ValueError(f"cannot multiply shapes {self.shape} and {other.shape}")
            cols = list(zip(*other._rows))
            return Matrix([[sum(a * b for a, b in zip(row, col)) for col in cols] for row in self._rows])
        if isinstance(other, Vector):
            if self.shape[1] != len(other):
                raise ValueError(f"cannot multiply shape {self.shape} by a vector of size {len(other)}")
            return Vector(*(sum(a * b for a, b in zip(row, other)) for row in self._rows))
        return NotImplemented

    def __rmatmul__(self, other):
        if isinstance(other, Vector):               # row vector times matrix
            if len(other) != self.shape[0]:
                raise ValueError(f"cannot multiply a vector of size {len(other)} by shape {self.shape}")
            return Vector(*(sum(a * b for a, b in zip(other, col)) for col in zip(*self._rows)))
        return NotImplemented

    def __pow__(self, n):
        if not isinstance(n, int) or isinstance(n, bool):
            return NotImplemented
        if n < 0:
            raise ValueError("negative powers are not supported")
        rows, cols = self.shape
        if rows != cols:
            raise ValueError("only square matrices can be raised to a power")
        result, base = Matrix.identity(rows), self
        while n:
            if n & 1:
                result = result @ base
            base = base @ base
            n >>= 1
        return result
```

## Complexity

Vector operations are O(n). `Matrix @ Matrix` for an (a x b) and (b x c) product is O(a*b*c). `m ** n` for a k x k matrix is O(k^3 log n) with repeated squaring instead of O(k^3 n). Memory is O(size of the result).

## Another way

Store matrices as one flat tuple with `rows` and `cols` and compute index `i * cols + j`: less memory and faster hashing. Make `Vector` a `typing.NamedTuple` or `tuple` subclass to get equality, hashing, iteration and indexing for free (but then `v + w` would be tuple concatenation unless you override it, and `v == (1, 2)` would be `True`). Real code uses `numpy` arrays, which implement the same operators in C.
