import pytest

from solution import Vector


def test_add():
    assert Vector(1, 2) + Vector(10, 20) == Vector(11, 22), "(1, 2) + (10, 20) should be (11, 22). Define __add__."


def test_sub():
    assert Vector(10, 20) - Vector(1, 2) == Vector(9, 18), "(10, 20) - (1, 2) should be (9, 18). Define __sub__."


def test_returns_new_object_and_inputs_unchanged():
    v, w = Vector(1, 2), Vector(3, 4)
    r = v + w
    assert r is not v and r is not w, "+ must build a NEW Vector, not return one of the operands."
    assert (v.x, v.y, w.x, w.y) == (1, 2, 3, 4), "+ must not change its operands. Do not write self.x += other.x."
    s = v - w
    assert (v.x, v.y) == (1, 2) and (w.x, w.y) == (3, 4), "- must not change its operands either."
    assert isinstance(s, Vector), "- must return a Vector."


def test_negative_and_float_values():
    assert Vector(-1, 0.5) + Vector(1, 0.25) == Vector(0, 0.75), "Mixed signs and floats should simply add per coordinate."


def test_chained():
    assert Vector(1, 1) + Vector(2, 2) + Vector(3, 3) - Vector(1, 1) == Vector(5, 5), "Because + returns a Vector, you can chain operators."


@pytest.mark.parametrize("bad", [5, "a", (1, 2), None])
def test_other_types_raise_typeerror(bad):
    with pytest.raises(TypeError):
        Vector(1, 2) + bad
    with pytest.raises(TypeError):
        Vector(1, 2) - bad


def test_returns_notimplemented():
    assert Vector(1, 2).__add__(5) is NotImplemented, "Return NotImplemented (do not raise) for non-Vector operands."
    assert Vector(1, 2).__sub__(5) is NotImplemented, "Return NotImplemented (do not raise) for non-Vector operands."
