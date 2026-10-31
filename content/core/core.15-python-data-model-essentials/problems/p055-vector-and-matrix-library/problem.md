# Project: a Vector and Matrix library

This is the **build** assessment of the module. You will write a small linear-algebra library using
the Python data model: `repr`, `format`, equality and hashing, the container protocols, and
operator overloading with the reflected methods and `NotImplemented`. Everything goes into
`solution.py`. Use only plain Python (no `numpy`). Both classes are **immutable**: no operation changes
its operands and there is no item assignment.

## `Vector`

| What | Behaviour |
|---|---|
| `Vector(*components)` | At least one component, all `int` or `float`. No component: `ValueError`. A non-number: `TypeError`. |
| `Vector.zeros(n)` | classmethod: `n` zeros. `n < 1` raises `ValueError`. |
| `len(v)`, `iter(v)`, `v[i]` | Number of components, the components, one component (negative indices too). `v[a:b]` returns a **Vector**. `v[0] = 1` fails with `TypeError`. |
| `repr(v)` / `str(v)` | `Vector(1, 2.5)` / `(1, 2.5)` |
| `format(v, spec)` | the spec is applied to **each** component: `f"{Vector(1, 2.5):.1f}"` is `(1.0, 2.5)`. |
| `==`, `hash` | Equal components (`Vector(1, 2) == Vector(1.0, 2.0)`). Other types: `NotImplemented`. Equal vectors have equal hashes. |
| `v + w`, `v - w` | Component by component. Different sizes raise `ValueError`. Other types: `NotImplemented` (so `v + 5` is a `TypeError`). |
| `-v`, `abs(v)`, `bool(v)` | Negation; the length `sqrt(sum of squares)`; `False` only for the zero vector. |
| `v * k`, `k * v`, `v / k` | `k` is an `int` or `float`; `k / v` and `v * w` are `TypeError`. |
| `v @ w` | The dot product, a **number**. Different sizes raise `ValueError`. |
| `sum([v1, v2, v3])` | Must work: `sum` starts from `0`, so `0 + v` must return `v`. Any other `x + v` is a `TypeError`. |

## `Matrix`

| What | Behaviour |
|---|---|
| `Matrix(rows)` | `rows` is any iterable of iterables of numbers. Must be non-empty, rectangular and made of numbers: `ValueError` or `TypeError` otherwise. It **copies** the data (a later change to the caller's lists does not change the matrix). |
| `Matrix.identity(n)` | classmethod; `n < 1` raises `ValueError`. |
| `m.shape` | property: `(rows, columns)`. |
| `len(m)`, `iter(m)` | Number of rows; the rows as **Vectors**. |
| `m[i]`, `m[i, j]` | Row `i` as a Vector; the single entry. Negative indices work. A slice raises `TypeError`, `m[0, 1, 2]` raises `TypeError`; item assignment raises `TypeError`. |
| `repr(m)` / `str(m)` | `Matrix([[1, 2], [3, 4]])` / one line per row, entries separated by one space (`"1 2\n3 4"`). |
| `==`, `hash` | Same entries. Other types: `NotImplemented`. |
| `m.transpose()`, `m.T` | The transposed matrix (`T` is a property). |
| `m + n`, `m - n`, `-m` | Entry by entry; different shapes raise `ValueError`. |
| `m * k`, `k * m` | Scalar multiplication. |
| `m @ n` | Matrix product (shape `(a, b) @ (b, c)` gives `(a, c)`); a mismatch raises `ValueError`. |
| `m @ v` | Matrix times a Vector gives a **Vector** (each row dotted with `v`). |
| `v @ m` | A Vector times a Matrix gives a Vector (`v` dotted with each **column**): this needs `Matrix.__rmatmul__`. |
| `m ** n` | `n` a non-negative `int`; `m ** 0` is the identity; `m` must be square (else `ValueError`); negative `n` raises `ValueError`; a non-int exponent is a `TypeError`. Use repeated multiplication (`m ** 30` must be fast). |

**Example**

```python
v, w = Vector(1, 2, 3), Vector(4, 5, 6)
v + w                    # Vector(5, 7, 9)
3 * v                    # Vector(3, 6, 9)
v @ w                    # 32
abs(Vector(3, 4))        # 5.0
sum([v, w])              # Vector(5, 7, 9)

a = Matrix([[1, 2], [3, 4]])
a @ Matrix([[5, 6], [7, 8]])   # Matrix([[19, 22], [43, 50]])
a @ Vector(1, 1)               # Vector(3, 7)
a.T                            # Matrix([[1, 3], [2, 4]])
Matrix([[1, 1], [1, 0]]) ** 10 # Matrix([[89, 55], [55, 34]])
```

## Advice

Work in the order of the test file: Vector basics, Vector equality, Vector arithmetic, Matrix
basics, Matrix arithmetic, the combined tests. Run the tests after each part. Write each operator so
that it returns `NotImplemented` (never raises `TypeError` yourself) for types it does not know: that
gives Python the chance to try the other operand's reflected method and produces the standard
error message.

## Ideas to go further (not tested)

`__getitem__` with slices for matrices (sub-matrices), `__iadd__` for a mutable version, `determinant()`
and `inverse()` for 2x2 matrices, a `Vector.normalized()`, `__array__`-like conversion to lists, comparing
floats with `math.isclose` in `__eq__`.
