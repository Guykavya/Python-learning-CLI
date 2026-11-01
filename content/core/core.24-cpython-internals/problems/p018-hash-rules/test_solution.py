import pytest

from solution import Point, check_hashable, hash_collisions, lost_keys


class Tag:
    """Hash depends on a mutable attribute: a bad key on purpose."""

    def __init__(self, name):
        self.name = name

    def __eq__(self, other):
        return isinstance(other, Tag) and self.name == other.name

    def __hash__(self):
        return len(self.name)

    def __repr__(self):
        return f"Tag({self.name!r})"


class EqOnly:
    def __eq__(self, other):
        return True


class Same:
    """All instances share one hash but are never equal to each other."""

    def __init__(self, n):
        self.n = n

    def __hash__(self):
        return 1234

    def __eq__(self, other):
        return isinstance(other, Same) and other.n == self.n

    def __repr__(self):
        return f"Same({self.n})"


def test_check_hashable_builtins():
    assert check_hashable(42) and check_hashable("text") and check_hashable(None)
    assert check_hashable(frozenset({1, 2})), "frozenset is the hashable, immutable set."
    assert not check_hashable([1]), "Lists are mutable, so hash() raises TypeError: return False."
    assert not check_hashable({}), "dicts are unhashable."
    assert not check_hashable({1}), "sets are unhashable."


def test_check_hashable_tuples():
    assert check_hashable((1, ("a", 2.5))), "A tuple of hashable things is hashable."
    assert not check_hashable((1, [2])), (
        "A tuple is hashable only if its items are: hash((1, [2])) raises TypeError. Call hash(), "
        "do not just check isinstance(obj, tuple)."
    )


def test_check_hashable_eq_without_hash():
    assert not check_hashable(EqOnly()), (
        "Defining __eq__ without __hash__ sets __hash__ to None, so the class is unhashable."
    )
    assert check_hashable(object()), "Plain objects hash by identity."


def test_point_as_key():
    d = {Point(1, 2): "here"}
    assert d[Point(1, 2)] == "here", (
        "A NEW Point(1, 2) must find the entry: equal points need equal hashes (hash the tuple (x, y))."
    )
    assert Point(1, 2) == Point(1, 2) and Point(1, 2) != Point(2, 1)
    assert hash(Point(3, 4)) == hash(Point(3, 4))
    assert len({Point(0, 0), Point(0, 0), Point(0, 1)}) == 2, "Duplicates collapse in a set."


def test_point_is_immutable():
    p = Point(1, 2)
    with pytest.raises(AttributeError):
        p.x = 5
    with pytest.raises(AttributeError):
        p.z = 0
    assert (p.x, p.y) == (1, 2), "A failed assignment must not change the point."


def test_point_repr_and_compare_to_other_types():
    assert repr(Point(1, 2)) == "Point(1, 2)", "repr must look like the constructor call."
    assert Point(1, 2) != (1, 2), "A Point is not equal to a plain tuple."


def test_lost_key():
    t = Tag("ab")
    d = {t: "found", "other": 1}
    t.name = "abc"
    assert t not in d, "Setup check: after the hash changed, the dict looks in the wrong slot."
    assert lost_keys(d) == [t], (
        "Iterating d still yields t, but `t in d` is False: such keys are lost. Compare iteration with lookup."
    )


def test_no_lost_keys_in_a_healthy_dict():
    d = {1: "a", "b": 2, (3, 4): 5, Point(1, 1): 6}
    assert lost_keys(d) == [], "When no key changed, every key is found again."


def test_lost_keys_order():
    a, b = Tag("x"), Tag("yy")
    d = {a: 1, "keep": 2, b: 3}
    a.name = "xxx"
    b.name = "yyyy"
    assert lost_keys(d) == [a, b], "Return the lost keys in the dict's iteration order."


def test_minus_one_collides_with_minus_two():
    assert hash_collisions([-1, -2]) == [[-1, -2]], (
        "hash(-1) == hash(-2) == -2 on every CPython, and -1 != -2: a real collision."
    )


def test_equal_values_are_one_value():
    assert hash_collisions([1, 1.0, True]) == [], (
        "1 == 1.0 == True and they share a hash: that is the equal-objects rule, not a collision."
    )
    assert hash_collisions([1, -1, 1.0, True, -2, 5]) == [[-1, -2]]


def test_custom_collisions_and_order():
    a, b, c = Same(1), Same(2), Same(1)
    got = hash_collisions([7, a, -1, b, c, -2])
    assert got == [[a, b], [-1, -2]], (
        f"Got {got}. Groups are ordered by their first value; inside a group keep input order and drop "
        "values equal to an earlier one (c == a)."
    )


def test_no_collisions():
    assert hash_collisions([]) == [] and hash_collisions([1, 2, 3]) == []
