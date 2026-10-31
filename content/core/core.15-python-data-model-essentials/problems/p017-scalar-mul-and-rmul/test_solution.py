import pytest

from solution import Vector


def test_mul_by_number():
    assert Vector(1, 2) * 3 == Vector(3, 6), "v * 3 should scale both coordinates: (3, 6). Define __mul__."


def test_rmul_number_on_the_left():
    assert 3 * Vector(1, 2) == Vector(3, 6), "3 * v needs __rmul__: Python asks int first, gets NotImplemented, then tries v.__rmul__(3)."


def test_float_scale():
    assert Vector(1, 2) * 0.5 == Vector(0.5, 1.0), "Scaling by a float should work: (0.5, 1.0)."
    assert 0.5 * Vector(1, 2) == Vector(0.5, 1.0), "0.5 * v needs __rmul__ too."


def test_div():
    assert Vector(1, 2) / 2 == Vector(0.5, 1.0), "v / 2 should be true division: (0.5, 1.0), not floor division."
    assert Vector(10, 20) / 10 == Vector(1, 2), "(10, 20) / 10 is (1.0, 2.0), which equals Vector(1, 2)."


def test_div_by_zero():
    with pytest.raises(ZeroDivisionError):
        Vector(1, 2) / 0


def test_no_change_to_operand():
    v = Vector(1, 2)
    v * 5
    5 * v
    assert (v.x, v.y) == (1, 2), "Operators must not change the Vector; return a new one."


def test_vector_times_vector_not_defined():
    with pytest.raises(TypeError):
        Vector(1, 2) * Vector(3, 4)


@pytest.mark.parametrize("bad", ["a", [1], None, (1, 2)])
def test_non_numbers_raise_typeerror(bad):
    with pytest.raises(TypeError):
        Vector(1, 2) * bad
    with pytest.raises(TypeError):
        bad * Vector(1, 2) if not isinstance(bad, (list, tuple, str)) else Vector(1, 2) * bad
    with pytest.raises(TypeError):
        Vector(1, 2) / bad
