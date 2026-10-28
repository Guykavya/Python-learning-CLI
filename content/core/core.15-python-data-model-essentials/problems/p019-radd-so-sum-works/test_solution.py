import pytest

from solution import Vector


def test_sum_of_vectors():
    vs = [Vector(1, 2), Vector(3, 4), Vector(5, 6)]
    assert sum(vs) == Vector(9, 12), "sum() starts with 0 + first_vector. Add __radd__ and accept 0."


def test_sum_of_one_item():
    assert sum([Vector(7, 8)]) == Vector(7, 8), "sum of one vector is that vector (0 + v = v)."


def test_zero_plus_vector():
    r = 0 + Vector(1, 1)
    assert isinstance(r, Vector) and r == Vector(1, 1), "0 + v should be a Vector equal to v."


def test_sum_generator():
    assert sum(Vector(i, i) for i in range(4)) == Vector(6, 6), "sum() over a generator works the same way."


def test_explicit_start_still_works():
    assert sum([Vector(1, 1), Vector(2, 2)], Vector(10, 10)) == Vector(13, 13), "An explicit start value must still work."


def test_empty_sum_is_zero():
    assert sum([]) == 0, "sum([]) is the int 0; that is not a Vector."


@pytest.mark.parametrize("left", [5, "a", None, 1.5, (1, 2)])
def test_other_left_operands_raise(left):
    with pytest.raises(TypeError):
        left + Vector(1, 1)


def test_radd_returns_notimplemented_for_others():
    assert Vector(1, 1).__radd__(5) is NotImplemented, "Only 0 is accepted on the left; return NotImplemented for everything else."


def test_does_not_mutate():
    v = Vector(1, 2)
    sum([v, Vector(1, 1)])
    assert (v.x, v.y) == (1, 2), "sum must not change the first vector."
