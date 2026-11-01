import pytest

from solution import ToySet


class Collide:
    """Every Collide has the same hash, so they all compete for the same slot."""

    def __init__(self, name):
        self.name = name

    def __hash__(self):
        return 42

    def __eq__(self, other):
        return isinstance(other, Collide) and self.name == other.name

    def __repr__(self):
        return f"Collide({self.name!r})"


class Counted:
    """Hash chosen by the test; counts how often == is called."""

    eq_calls = 0

    def __init__(self, h):
        self.h = h

    def __hash__(self):
        return self.h

    def __eq__(self, other):
        Counted.eq_calls += 1
        return isinstance(other, Counted) and self.h == other.h


# ------------------------------------------------------------------ basics
def test_empty():
    s = ToySet()
    assert len(s) == 0 and list(s) == [] and 1 not in s, "A new ToySet is empty."
    assert s.capacity == 8, "The table starts with 8 slots."


def test_add_and_contains():
    s = ToySet()
    s.add("a")
    s.add("b")
    assert "a" in s and "b" in s and "c" not in s, "__contains__ must find added items and nothing else."
    assert len(s) == 2


def test_no_duplicates():
    s = ToySet([1, 2, 2, 3, 3, 3])
    assert len(s) == 3, "Adding an item that is already there changes nothing."
    assert sorted(s) == [1, 2, 3], "__iter__ yields every item exactly once."


def test_equal_but_not_identical():
    s = ToySet()
    s.add(1)
    s.add(1.0)
    assert len(s) == 1 and True in s, "1, 1.0 and True are equal and have the same hash, so they are one item."


def test_unhashable():
    s = ToySet()
    with pytest.raises(TypeError):
        s.add([1, 2])
    with pytest.raises(TypeError):
        [1] in s  # noqa: B015 - the lookup itself must raise
    assert len(s) == 0, "Call hash(item) first: a list has no hash, and nothing must be stored."


def test_many_items():
    s = ToySet(range(0, 20_000, 2))
    assert len(s) == 10_000
    assert all(i in s for i in range(0, 20_000, 2)), "Every added item must still be found after many resizes."
    assert not any(i in s for i in range(1, 20_000, 2)), "Items never added must not be found."


def test_negative_and_big_hashes():
    items = [-1, -2, -8, 2**40, -(2**40), "hello", (1, 2)]
    s = ToySet(items)
    assert all(x in s for x in items), "Use hash & (capacity - 1) (or % capacity) so negative hashes map to a valid slot."


# ------------------------------------------------------------------ collisions and tombstones
def test_collisions():
    items = [Collide(c) for c in "abcdefghij"]
    s = ToySet(items)
    assert len(s) == 10, "Items with equal hashes but different values are different items: probe to the next slot."
    assert all(Collide(c) in s for c in "abcdefghij"), "Lookups must probe past slots holding other colliding items."
    assert Collide("z") not in s, "A missing item with a colliding hash is not found (stop at an EMPTY slot)."


def test_remove_keeps_the_chain():
    s = ToySet([Collide("a"), Collide("b"), Collide("c")])
    s.remove(Collide("a"))
    assert Collide("b") in s and Collide("c") in s, (
        "Removing must leave a tombstone (a 'deleted' marker), not an empty slot. An empty slot would stop "
        "the probe early and 'lose' b and c, which sit further along the chain."
    )
    assert Collide("a") not in s and len(s) == 2


def test_readd_after_remove_no_duplicate():
    s = ToySet([Collide("a"), Collide("b")])
    s.remove(Collide("a"))
    s.add(Collide("b"))
    assert len(s) == 1, (
        "b is already further along the chain. Before reusing the first tombstone you meet, keep probing "
        "to check that the item is not already in the set."
    )
    assert [x.name for x in s] == ["b"]


def test_tombstone_reused_or_cleaned():
    s = ToySet()
    for i in range(1_000):
        s.add(i)
        s.remove(i)
    assert len(s) == 0
    assert 5 not in s, "Lookups must end even when many slots hold tombstones (count them in the load)."
    assert s.capacity == 8, (
        "Resizing rebuilds the table from the LIVE items only, choosing the smallest power of two (at least 8) "
        "that fits them; tombstones are dropped. Repeated add/remove must not keep doubling the table."
    )


def test_compares_hash_before_eq():
    Counted.eq_calls = 0
    s = ToySet([Counted(1), Counted(9)])  # 1 and 9 land in the same slot of an 8-slot table
    Counted.eq_calls = 0
    assert Counted(9) in s
    assert Counted.eq_calls == 1, (
        "Store each item's hash next to it and call == only when the stored hash equals the hash you look "
        "for (like CPython). Comparing with Counted(1) is wasted work: different hashes mean different items."
    )


def test_identity_shortcut():
    nan = float("nan")
    s = ToySet([nan])
    assert nan in s, "nan != nan, but CPython checks `stored is item` before ==. Do the same."


# ------------------------------------------------------------------ resizing
def test_resize_rule():
    s = ToySet()
    for i in range(5):
        s.add(i)
    assert s.capacity == 8, "The first 5 adds fit in 8 slots: before the 5th, (fill + 1) * 3 = 15 <= 8 * 2."
    s.add(5)
    assert s.capacity == 16, "Before adding a NEW item, resize if (fill + 1) * 3 > capacity * 2: the 6th add grows to 16."


def test_load_factor_stays_below_two_thirds():
    s = ToySet()
    for i in range(1_000):
        s.add(i * 7)
        assert len(s) * 3 <= s.capacity * 2, "The table must never be more than 2/3 full."
    cap = s.capacity
    assert cap & (cap - 1) == 0, "Capacity stays a power of two, so hash & (capacity - 1) picks a slot."


def test_adding_existing_item_does_not_resize():
    s = ToySet(range(5))
    s.add(3)
    assert s.capacity == 8, "Adding an item that is already present must not count as a new item."


def test_remove_and_discard():
    s = ToySet([1, 2, 3])
    s.discard(99)
    s.discard(2)
    assert sorted(s) == [1, 3], "discard removes the item if present, and silently does nothing otherwise."
    with pytest.raises(KeyError):
        s.remove(99)
    s.remove(1)
    assert sorted(s) == [3] and len(s) == 1


# ------------------------------------------------------------------ set algebra
def test_union_intersection_difference():
    a = ToySet([1, 2, 3, 4])
    b = ToySet([3, 4, 5])
    for result, expected, name in [
        (a.union(b), {1, 2, 3, 4, 5}, "union"),
        (a.intersection(b), {3, 4}, "intersection"),
        (a.difference(b), {1, 2}, "difference"),
        (b.difference(a), {5}, "difference (other way)"),
    ]:
        assert isinstance(result, ToySet), f"{name} returns a new ToySet."
        assert sorted(result) == sorted(expected) and len(result) == len(expected), f"{name} is wrong."
    assert sorted(a) == [1, 2, 3, 4] and sorted(b) == [3, 4, 5], "The set operations must not change a or b."


def test_operators_and_plain_iterables():
    a = ToySet("abc")
    assert sorted(a | ToySet("cd")) == list("abcd"), "| is union."
    assert sorted(a & ToySet("bcz")) == list("bc"), "& is intersection."
    assert sorted(a - ToySet("a")) == list("bc"), "- is difference."
    assert sorted(a.union(["x", "a"])) == list("abcx"), "The methods accept any iterable, like set.union."
    assert sorted(a.intersection(["a", "q"])) == ["a"]


def test_equality():
    assert ToySet([1, 2, 3]) == ToySet([3, 2, 1]), "Sets with the same items are equal, whatever the order."
    assert ToySet([1, 2]) != ToySet([1, 2, 3])
    assert ToySet([1, 2]) == {1, 2}, "A ToySet can also be compared with a built-in set."
