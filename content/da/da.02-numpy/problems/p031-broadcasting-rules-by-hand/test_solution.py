import numpy as np
import numpy.random  # load it before the helpers are switched off
import pytest

from solution import broadcast_shape

REAL = np.broadcast_shapes   # saved before the helpers are switched off


def _forbidden(*args, **kwargs):
    raise AssertionError("this problem is about the rules: compute the shape yourself, without NumPy's broadcast helpers.")


@pytest.fixture(autouse=True)
def no_helpers(monkeypatch):
    for name in ("broadcast_shapes", "broadcast_to", "broadcast_arrays"):
        monkeypatch.setattr(np, name, _forbidden)


def first_bad_axis(shapes):
    ndim = max(len(s) for s in shapes)
    padded = [(1,) * (ndim - len(s)) + tuple(s) for s in shapes]
    for axis in range(ndim - 1, -1, -1):
        if len({s[axis] for s in padded} - {1}) > 1:
            return axis
    return None


def test_the_examples():
    got = broadcast_shape((3, 1), (4,))
    assert isinstance(got, tuple), f"return a tuple, not a {type(got).__name__}."
    assert got == (3, 4), f"(3, 1) with (4,): (4,) is padded to (1, 4); result (3, 4). Got {got}."
    assert broadcast_shape((5, 1, 4), (3, 1)) == (5, 3, 4), "(5, 1, 4) with (3, 1) -> (5, 3, 4): pad on the LEFT."
    assert broadcast_shape((2, 1), (1, 3), (4, 1, 1)) == (4, 2, 3), "three shapes at once -> (4, 2, 3): every shape takes part."
    assert broadcast_shape((8, 1, 6, 1), (7, 1, 5)) == (8, 7, 6, 5), "(8, 1, 6, 1) with (7, 1, 5) -> (8, 7, 6, 5)."


def test_no_shapes_and_one_shape():
    assert broadcast_shape() == (), "no shapes at all: return () (max() of an empty sequence raises: handle it first)."
    assert broadcast_shape((2, 3)) == (2, 3), "one shape broadcasts to itself."
    got = broadcast_shape([2, 3])
    assert got == (2, 3) and isinstance(got, tuple), f"a list shape must come back as a tuple, got {got!r}."
    assert broadcast_shape((), (2, 2)) == (2, 2), "() is a scalar: it broadcasts with anything."
    assert broadcast_shape((), ()) == (), "two scalars give ()."


def test_zero_length_axes():
    assert broadcast_shape((0,), (1,)) == (0,), "a length-1 axis stretches to 0 too: (0,) with (1,) is (0,). Did you use max()?"
    assert broadcast_shape((3, 0), (3, 1)) == (3, 0), "(3, 0) with (3, 1) -> (3, 0)."
    with pytest.raises(ValueError):
        broadcast_shape((0,), (3,))


def test_result_contains_plain_ints():
    got = broadcast_shape((np.int64(2), 1), (3,))
    assert got == (2, 3), f"expected (2, 3), got {got}."
    assert all(type(n) is int for n in got), f"return plain Python ints, got {[type(n).__name__ for n in got]}."


@pytest.mark.parametrize("shapes, axis", [
    (((2, 3), (3, 2)), 1),
    (((4, 3), (4,)), 1),
    (((3, 4), (3, 4, 1)), 1),
    (((2, 5, 3), (4, 1, 3)), 0),
    (((2, 1), (1, 3), (4, 2, 2)), 2),
])
def test_incompatible_shapes_name_the_axis(shapes, axis):
    with pytest.raises(ValueError) as info:
        broadcast_shape(*shapes)
    msg = str(info.value)
    assert f"axis {axis}" in msg, (
        f"shapes {shapes}: the first clash met from the right is at axis {axis} of the padded result; "
        f"your message was {msg!r}. Count axes from the left after padding.")


def random_shapes(rng):
    base = [int(rng.choice([1, 2, 3, 4, 5, 0], p=[0.25, 0.25, 0.2, 0.15, 0.1, 0.05])) for _ in range(int(rng.integers(0, 5)))]
    shapes = []
    for _ in range(int(rng.integers(2, 4))):
        k = int(rng.integers(0, len(base) + 1))
        s = [1 if rng.random() < 0.3 else v for v in base[len(base) - k:]]
        if s and rng.random() < 0.25:
            s[int(rng.integers(0, len(s)))] = int(rng.integers(1, 6))
        shapes.append(tuple(s))
    return shapes


def test_two_hundred_random_cases_against_numpy():
    rng = np.random.default_rng(31)
    for _ in range(200):
        shapes = random_shapes(rng)
        try:
            want = REAL(*shapes)
        except ValueError:
            want = None
        if want is None:
            with pytest.raises(ValueError) as info:
                broadcast_shape(*shapes)
            axis = first_bad_axis(shapes)
            assert f"axis {axis}" in str(info.value), f"{shapes}: expected the message to name axis {axis}, got {str(info.value)!r}."
        else:
            got = broadcast_shape(*shapes)
            assert got == want, f"shapes {shapes}: NumPy gives {want}, you gave {got}."
