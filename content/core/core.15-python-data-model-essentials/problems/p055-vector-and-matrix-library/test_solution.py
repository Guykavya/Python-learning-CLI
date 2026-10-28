import math

import pytest

from solution import Matrix, Vector


def V(*c):
    return Vector(*c)


def M(*rows):
    return Matrix(list(rows))


# =============================================================== Part 1: Vector basics
def test_vector_construction_and_validation():
    assert Vector(1, 2, 3)[0] == 1, "Vector(1, 2, 3) stores its components; v[0] is the first."
    with pytest.raises(ValueError):
        Vector()
    with pytest.raises(TypeError):
        Vector(1, "a")
    with pytest.raises(TypeError):
        Vector(1, None)
    assert Vector(0.5, -2) is not None, "Floats and negative numbers are fine."


def test_vector_zeros():
    assert Vector.zeros(3) == Vector(0, 0, 0), "Vector.zeros(n) is a classmethod returning n zeros."
    with pytest.raises(ValueError):
        Vector.zeros(0)


def test_vector_container_protocol():
    v = V(4, 5, 6)
    assert len(v) == 3, "len(v) is the number of components (define __len__)."
    assert list(v) == [4, 5, 6], "Iterating a Vector yields its components (define __iter__)."
    assert v[-1] == 6, "Negative indices work like in a tuple."
    assert v[0:2] == V(4, 5), "A slice returns a new Vector, not a tuple."
    assert isinstance(v[1:], Vector), "Slicing must return a Vector."
    with pytest.raises(IndexError):
        v[3]
    x, y, z = v
    assert (x, y, z) == (4, 5, 6), "Unpacking works through __iter__."
    assert 5 in v and 9 not in v and max(v) == 6, "`in` and max() work through __iter__."


def test_vector_repr_str_format():
    assert repr(V(1, 2.5)) == "Vector(1, 2.5)", "repr(Vector(1, 2.5)) should be 'Vector(1, 2.5)': the constructor call."
    assert str(V(1, 2)) == "(1, 2)", "str() is the components in parentheses: (1, 2)."
    assert f"{V(1, 2.5):.1f}" == "(1.0, 2.5)", "format spec is applied to every component: define __format__ and use format(component, spec)."
    assert f"{V(1, 2)}" == "(1, 2)", "An empty format spec gives the same text as str()."
    assert eval(repr(V(3, -4))) == V(3, -4), "eval(repr(v)) should rebuild an equal vector."


# =============================================================== Part 2: Vector equality and hashing
def test_vector_equality():
    assert V(1, 2) == V(1, 2), "Vectors with the same components are equal (define __eq__)."
    assert V(1, 2) != V(2, 1) and V(1, 2) != V(1, 2, 0), "Order and length matter."
    assert V(1, 2) == V(1.0, 2.0), "1 == 1.0 so the vectors are equal."
    assert (V(1, 2) == (1, 2)) is False, "A Vector is not equal to a tuple: return NotImplemented for other types."
    assert V(1) != "x", "Comparing with an unrelated object gives False, not an exception."


def test_vector_hash_consistent_with_eq():
    assert hash(V(1, 2)) == hash(V(1.0, 2.0)), "Equal vectors must have equal hashes: hash the tuple of components."
    assert len({V(1, 2), V(1, 2), V(2, 1)}) == 2, "Vectors work in sets once __hash__ exists."
    assert {V(0, 1): "a"}[V(0, 1)] == "a", "Vectors work as dict keys."


# =============================================================== Part 3: Vector arithmetic
def test_vector_add_sub_neg():
    assert V(1, 2) + V(10, 20) == V(11, 22), "v + w adds component by component."
    assert V(5, 5) - V(1, 2) == V(4, 3), "v - w subtracts component by component (order matters)."
    assert -V(1, -2) == V(-1, 2), "-v negates every component (define __neg__)."
    assert V(1, 2) + V(0, 0) == V(1, 2), "Adding the zero vector changes nothing."


def test_vector_arithmetic_errors():
    with pytest.raises(ValueError):
        V(1, 2) + V(1, 2, 3)
    with pytest.raises(ValueError):
        V(1, 2) - V(1)
    with pytest.raises(TypeError):
        V(1, 2) + 5
    with pytest.raises(TypeError):
        V(1, 2) + (1, 2)
    with pytest.raises(TypeError):
        5 - V(1, 2)
    with pytest.raises(TypeError):
        V(1, 2) * V(3, 4)


def test_vector_scalar_multiplication_both_sides():
    assert V(1, 2) * 3 == V(3, 6), "v * k multiplies every component (define __mul__)."
    assert 3 * V(1, 2) == V(3, 6), "k * v needs __rmul__: int.__mul__ returns NotImplemented and Python tries v.__rmul__(k)."
    assert 0.5 * V(4, 8) == V(2.0, 4.0), "Floats work as scalars."
    assert V(1, 2) * 0 == V(0, 0), "Multiplying by 0 gives the zero vector."


def test_vector_division_by_scalar():
    assert V(4, 6) / 2 == V(2.0, 3.0), "v / k divides every component (define __truediv__)."
    with pytest.raises(ZeroDivisionError):
        V(1, 2) / 0
    with pytest.raises(TypeError):
        2 / V(1, 2)


def test_vector_dot_product_with_matmul():
    assert V(1, 2, 3) @ V(4, 5, 6) == 32, "v @ w is the dot product: 1*4 + 2*5 + 3*6 = 32, a plain number (not a Vector)."
    assert V(1, 0) @ V(0, 1) == 0, "Perpendicular vectors have dot product 0."
    with pytest.raises(ValueError):
        V(1, 2) @ V(1, 2, 3)
    with pytest.raises(TypeError):
        V(1, 2) @ 3


def test_vector_abs_and_bool():
    assert abs(V(3, 4)) == 5.0, "abs(v) is the length: sqrt(3*3 + 4*4) = 5.0 (define __abs__)."
    assert math.isclose(abs(V(1, 1)), math.sqrt(2)), "abs of (1, 1) is sqrt(2)."
    assert bool(V(0, 0, 0)) is False, "The zero vector is falsy: define __bool__ (len() would say 3, which is truthy)."
    assert bool(V(0, 0.1)) is True, "A vector with any non-zero component is truthy."


def test_sum_of_vectors_needs_radd():
    vs = [V(1, 1), V(2, 2), V(3, 3)]
    assert sum(vs) == V(6, 6), "sum() starts with the int 0 and does 0 + V(1, 1): define __radd__ so that adding 0 returns the vector itself."
    assert sum([V(7, 8)]) == V(7, 8), "One vector: 0 + v."
    with pytest.raises(TypeError):
        3 + V(1, 1)


def test_vector_is_immutable():
    v = V(1, 2)
    with pytest.raises(TypeError):
        v[0] = 9
    with pytest.raises(TypeError):
        del v[0]
    assert v == V(1, 2), "Operations never change the vectors they read."
    w = v + V(1, 1)
    assert v == V(1, 2) and w == V(2, 3), "v + w returns a NEW vector; v keeps its value."


def test_vector_operands_are_not_modified():
    a, b = V(1, 2), V(3, 4)
    a + b, a - b, a * 2, 2 * a, -a, a / 2, a @ b
    assert a == V(1, 2) and b == V(3, 4), "No operator may change its operands."


# =============================================================== Part 4: Matrix basics
def test_matrix_construction_and_shape():
    m = M([1, 2, 3], [4, 5, 6])
    assert m.shape == (2, 3), "shape is (rows, columns): a property returning a tuple."
    assert Matrix([(1, 2), (3, 4)]).shape == (2, 2), "Rows can be tuples or lists."
    assert Matrix(iter([[1], [2], [3]])).shape == (3, 1), "Any iterable of rows works (a generator too)."


def test_matrix_validation():
    with pytest.raises(ValueError):
        Matrix([])
    with pytest.raises(ValueError):
        Matrix([[]])
    with pytest.raises(ValueError):
        Matrix([[1, 2], [3]])
    with pytest.raises(TypeError):
        Matrix([[1, "a"]])


def test_matrix_does_not_alias_the_input():
    rows = [[1, 2], [3, 4]]
    m = Matrix(rows)
    rows[0][0] = 99
    assert m[0, 0] == 1, "Copy the rows into tuples: later changes to the caller's lists must not change the matrix."


def test_matrix_identity():
    assert Matrix.identity(3) == M([1, 0, 0], [0, 1, 0], [0, 0, 1]), "identity(n) has 1 on the diagonal and 0 elsewhere."
    with pytest.raises(ValueError):
        Matrix.identity(0)


def test_matrix_indexing():
    m = M([1, 2, 3], [4, 5, 6])
    assert m[0, 2] == 3 and m[1, 0] == 4, "m[i, j] is a single entry (the key is the tuple (i, j))."
    assert m[1] == V(4, 5, 6), "m[i] is the row i as a Vector."
    assert m[-1, -1] == 6 and m[-1] == V(4, 5, 6), "Negative indices work."
    with pytest.raises(IndexError):
        m[2]
    with pytest.raises(IndexError):
        m[0, 3]
    with pytest.raises(TypeError):
        m[0, 1, 2]


def test_matrix_len_and_iteration_give_rows():
    m = M([1, 2], [3, 4], [5, 6])
    assert len(m) == 3, "len(m) is the number of rows."
    rows = list(m)
    assert rows == [V(1, 2), V(3, 4), V(5, 6)], "Iterating a Matrix yields its rows as Vectors."
    assert all(isinstance(r, Vector) for r in rows), "Rows are Vector objects."
    assert [sum(r) for r in m] == [3, 7, 11], "Because rows are iterable Vectors, sum(row) works."


def test_matrix_repr_str():
    m = M([1, 2], [3, 4])
    assert repr(m) == "Matrix([[1, 2], [3, 4]])", "repr(m) should be 'Matrix([[1, 2], [3, 4]])': the constructor call with lists."
    assert str(m) == "1 2\n3 4", "str(m) is one line per row, entries separated by one space."
    assert eval(repr(m)) == m, "eval(repr(m)) should rebuild an equal matrix."


def test_matrix_equality_and_hash():
    assert M([1, 2], [3, 4]) == M([1.0, 2.0], [3.0, 4.0]), "Same entries means equal."
    assert M([1, 2]) != M([1], [2]), "Different shapes are never equal."
    assert (M([1]) == 1) is False and (M([1]) == [[1]]) is False, "A Matrix is not equal to unrelated objects (return NotImplemented)."
    assert hash(M([1, 2], [3, 4])) == hash(M([1.0, 2.0], [3.0, 4.0])), "Equal matrices have equal hashes."
    assert len({M([1]), M([1]), M([2])}) == 2, "Matrices work in sets."


def test_matrix_is_immutable():
    m = M([1, 2], [3, 4])
    with pytest.raises(TypeError):
        m[0, 0] = 5
    with pytest.raises(TypeError):
        m[0] = V(0, 0)


# =============================================================== Part 5: Matrix arithmetic
def test_transpose():
    m = M([1, 2, 3], [4, 5, 6])
    assert m.transpose() == M([1, 4], [2, 5], [3, 6]), "transpose() swaps rows and columns."
    assert m.T == m.transpose(), "`.T` is a property that gives the same result."
    assert m.T.T == m, "Transposing twice gives the original."
    assert m.T.shape == (3, 2), "Shape (2, 3) becomes (3, 2)."


def test_matrix_add_sub_neg():
    a, b = M([1, 2], [3, 4]), M([10, 20], [30, 40])
    assert a + b == M([11, 22], [33, 44]), "m + n adds entry by entry."
    assert b - a == M([9, 18], [27, 36]), "m - n subtracts entry by entry."
    assert -a == M([-1, -2], [-3, -4]), "-m negates every entry."
    with pytest.raises(ValueError):
        a + M([1, 2, 3], [4, 5, 6])
    with pytest.raises(ValueError):
        a - M([1, 2])
    with pytest.raises(TypeError):
        a + 1
    with pytest.raises(TypeError):
        a + V(1, 2)
    assert a == M([1, 2], [3, 4]), "Operands are not modified."


def test_matrix_scalar_multiplication():
    m = M([1, 2], [3, 4])
    assert m * 2 == M([2, 4], [6, 8]), "m * k scales every entry."
    assert 2 * m == M([2, 4], [6, 8]), "k * m needs __rmul__."
    assert m * 0.5 == M([0.5, 1.0], [1.5, 2.0]), "Floats work."
    with pytest.raises(TypeError):
        m * m
    with pytest.raises(TypeError):
        m * V(1, 2)


def test_matrix_times_matrix():
    a = M([1, 2], [3, 4])
    b = M([5, 6], [7, 8])
    assert a @ b == M([19, 22], [43, 50]), "(a @ b)[i][j] is row i of a dotted with column j of b: [[1*5+2*7, 1*6+2*8], [3*5+4*7, 3*6+4*8]]."
    assert b @ a == M([23, 34], [31, 46]), "Matrix multiplication is NOT commutative: b @ a differs from a @ b."
    assert a @ Matrix.identity(2) == a and Matrix.identity(2) @ a == a, "Multiplying by the identity changes nothing."


def test_matrix_times_matrix_shapes():
    a = M([1, 2, 3], [4, 5, 6])            # 2 x 3
    b = M([1, 0], [0, 1], [1, 1])          # 3 x 2
    assert (a @ b).shape == (2, 2) and a @ b == M([4, 5], [10, 11]), "A (2x3) times B (3x2) is 2x2."
    assert (b @ a).shape == (3, 3), "B (3x2) times A (2x3) is 3x3."
    with pytest.raises(ValueError):
        a @ a
    with pytest.raises(TypeError):
        a @ 3


def test_matrix_times_vector_and_vector_times_matrix():
    m = M([1, 2], [3, 4], [5, 6])           # 3 x 2
    assert m @ V(1, 1) == V(3, 7, 11), "m @ v gives a Vector: each row dotted with v."
    assert V(1, 1, 1) @ m == V(9, 12), "v @ m (row vector times matrix) gives a Vector: v dotted with each COLUMN. Define __rmatmul__ on Matrix."
    with pytest.raises(ValueError):
        m @ V(1, 2, 3)
    with pytest.raises(ValueError):
        V(1, 2) @ m


def test_matrix_power():
    m = M([1, 1], [1, 0])
    assert m ** 0 == Matrix.identity(2), "m ** 0 is the identity matrix."
    assert m ** 1 == m, "m ** 1 is m."
    assert m ** 5 == M([8, 5], [5, 3]), "Fibonacci matrix: m ** 5 is [[8, 5], [5, 3]] (repeated m @ m)."
    assert m ** 30 == M([1346269, 832040], [832040, 514229]), "m ** 30 holds Fibonacci numbers: fast enough with repeated multiplication."
    with pytest.raises(ValueError):
        M([1, 2, 3]) ** 2
    with pytest.raises(ValueError):
        m ** -1
    with pytest.raises(TypeError):
        m ** 0.5


# =============================================================== Part 6: everything together
def test_rotation_example():
    rotate90 = M([0, -1], [1, 0])
    assert rotate90 @ V(1, 0) == V(0, 1), "Rotating (1, 0) by 90 degrees gives (0, 1)."
    assert (rotate90 ** 4) == Matrix.identity(2), "Four 90 degree turns are the identity."
    assert rotate90 @ (rotate90 @ V(2, 3)) == (rotate90 @ rotate90) @ V(2, 3), "(A @ A) @ v equals A @ (A @ v): associativity."


def test_linear_algebra_identities():
    a, b = M([1, 2], [3, 4]), M([0, 1], [1, 0])
    v = V(2, -1)
    assert (a + b) @ v == a @ v + b @ v, "(A + B) v == A v + B v."
    assert (a @ b).T == b.T @ a.T, "Transpose reverses the order: (AB)^T == B^T A^T."
    assert (2 * a) @ v == 2 * (a @ v), "Scalars can be moved out."
    assert sum(r @ v for r in a) == (V(1, 1) @ a) @ v, "Summing row dot products equals (1,1) @ A then dot with v."


def test_dot_product_rows_and_columns_through_the_protocols():
    m = M([1, 2], [3, 4])
    columns = [Vector(*col) for col in zip(*m)]
    assert columns == [V(1, 3), V(2, 4)], "zip(*m) works because iterating m gives rows and each row is iterable."
    assert max(abs(r) for r in m) == pytest.approx(5.0), "abs() works on rows, and max() on a generator of them."
