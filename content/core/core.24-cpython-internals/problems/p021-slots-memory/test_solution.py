import sys

import pytest

from solution import Plain, Slotted, compare_memory, instance_size

# No exact byte counts anywhere: they differ between Python versions and platforms.


def test_classes_store_attributes():
    p, s = Plain(1, 2, 3), Slotted(4, 5, 6)
    assert (p.x, p.y, p.z) == (1, 2, 3)
    assert (s.x, s.y, s.z) == (4, 5, 6)


def test_slotted_has_no_dict():
    s = Slotted(1, 2, 3)
    assert not hasattr(s, "__dict__"), "Slotted needs __slots__ = ('x', 'y', 'z'), which removes the __dict__."
    with pytest.raises(AttributeError):
        s.w = 4
    assert hasattr(Plain(1, 2, 3), "__dict__"), "Plain must be an ordinary class with a __dict__."


def test_instance_size_of_plain_includes_dict():
    p = Plain(1, 2, 3)
    d = vars(p)                       # make sure the dict exists before measuring
    expected = sys.getsizeof(p) + sys.getsizeof(d)
    assert instance_size(p) == expected, (
        "For an object with a __dict__, add sys.getsizeof(obj.__dict__) to sys.getsizeof(obj): "
        "getsizeof does not count the attribute dictionary."
    )


def test_instance_size_of_slotted():
    s = Slotted(1, 2, 3)
    assert instance_size(s) == sys.getsizeof(s), "A slotted object has no __dict__: its size is just getsizeof(obj)."


def test_instance_size_of_builtins():
    assert instance_size(12345) == sys.getsizeof(12345), "An int has no __dict__."
    assert instance_size([1, 2]) == sys.getsizeof([1, 2]), "A list has no __dict__."


def test_slots_are_smaller():
    plain, slotted = compare_memory(500)
    assert slotted > 0 and plain > 0, "Both totals must be positive byte counts."
    assert plain > slotted, (
        f"Plain total {plain} is not bigger than Slotted total {slotted}. Did you forget the __dict__ "
        "in instance_size, or the __slots__ in Slotted?"
    )


def test_totals_add_up():
    n = 300
    plain, slotted = compare_memory(n)
    one_slotted = sys.getsizeof(Slotted(0, 0, 0))
    assert slotted == n * one_slotted, (
        "All Slotted instances have the same size, so the total must be n * getsizeof(one instance). "
        "Did you create n of them?"
    )
    one_plain_object = sys.getsizeof(Plain(0, 0, 0))
    assert plain > n * one_plain_object, (
        "The Plain total must include every instance's __dict__, so it is more than n * getsizeof(object)."
    )


def test_scales_with_n():
    p1, s1 = compare_memory(100)
    p2, s2 = compare_memory(200)
    assert s2 == 2 * s1, "Twice as many slotted objects use exactly twice the bytes."
    assert p2 > p1, "More Plain objects use more bytes."


def test_zero():
    assert compare_memory(0) == (0, 0), "No objects, no bytes."
