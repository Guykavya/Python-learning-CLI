import math

from solution import Vector


def test_neg():
    assert -Vector(3, -4) == Vector(-3, 4), "-v should negate both coordinates. Define __neg__."


def test_neg_returns_new_object():
    v = Vector(1, 2)
    r = -v
    assert r is not v and (v.x, v.y) == (1, 2), "-v must build a new Vector and leave v alone."


def test_pos():
    v = Vector(1, -2)
    assert +v == v, "+v should equal v. Define __pos__."
    assert (+v) is not v, "+v should return a new Vector, not the same object."


def test_abs_is_length():
    assert abs(Vector(3, 4)) == 5.0, "abs(Vector(3, 4)) is the length 5.0. Define __abs__."
    assert math.isclose(abs(Vector(-1, -1)), math.sqrt(2)), "abs of (-1, -1) is sqrt(2); negative values still give a positive length."
    assert isinstance(abs(Vector(0, 0)), float) or abs(Vector(0, 0)) == 0, "abs of the zero vector is 0."


def test_bool_zero_vector_is_false():
    assert bool(Vector(0, 0)) is False, "Only the zero vector is falsy. Define __bool__."
    assert not Vector(0, 0), "`not v` should be True for the zero vector."


def test_bool_nonzero_is_true():
    assert bool(Vector(0, 1)) is True, "Vector(0, 1) is not the zero vector, so it is truthy."
    assert bool(Vector(2, 0)) is True, "Vector(2, 0) is not the zero vector, so it is truthy."
    assert bool(Vector(-1, -1)) is True, "Negative coordinates are non zero."


def test_filter_none():
    items = [Vector(0, 0), Vector(1, 0), Vector(0, 0), Vector(0, 2)]
    assert len(list(filter(None, items))) == 2, "filter(None, items) keeps truthy items, so it relies on __bool__."
