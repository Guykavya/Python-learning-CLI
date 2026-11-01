import random

import pytest

from solution import DELETED, ToyDict


class Collide:
    """Every instance has the same hash, so they all fight for the same slot."""

    def __init__(self, n):
        self.n = n

    def __hash__(self):
        return 7

    def __eq__(self, other):
        return isinstance(other, Collide) and self.n == other.n

    def __repr__(self):
        return f"Collide({self.n})"


def test_set_and_get():
    d = ToyDict()
    d["a"] = 1
    d["b"] = 2
    assert d["a"] == 1 and d["b"] == 2, "Values must come back from the keys they were stored under."
    assert len(d) == 2


def test_missing_key_raises_key_error():
    d = ToyDict()
    d[1] = "x"
    with pytest.raises(KeyError):
        d[2]
    with pytest.raises(KeyError):
        del d[2]
    assert d.get(2) is None and d.get(2, "dflt") == "dflt", "get returns the default for a missing key."
    assert 2 not in d and 1 in d, "__contains__ must use the same lookup."


def test_linear_probing_layout():
    d = ToyDict()
    d[1] = "a"
    d[9] = "b"
    assert d.indices[1] == 0, "hash(1) & 7 == 1, so entry 0 goes into slot 1."
    assert d.indices[2] == 1, (
        "hash(9) & 7 == 1 is taken, so linear probing puts entry 1 into the NEXT slot, 2."
    )
    assert d.entries == [[1, 1, "a"], [9, 9, "b"]], "entries hold [hash, key, value] in insertion order."


def test_probing_wraps_around():
    d = ToyDict()
    d[7] = "a"
    d[15] = "b"
    assert d.indices[7] == 0 and d.indices[0] == 1, (
        "15 & 7 == 7 is taken; the next slot wraps around to 0: use (slot + 1) & (capacity - 1)."
    )
    assert d[15] == "b"


def test_update_keeps_position():
    d = ToyDict()
    d["x"] = 1
    d["y"] = 2
    d["x"] = 10
    assert list(d) == ["x", "y"] and d["x"] == 10, "Setting an existing key changes the value in place; order stays."
    assert len(d.entries) == 2, "Updating must not append a second entry for the same key."


def test_delete_leaves_tombstone():
    d = ToyDict()
    d[1] = "a"
    d[9] = "b"
    del d[1]
    assert d.indices[1] is DELETED, "Deleting puts the DELETED marker in the slot (not None)."
    assert d.entries[0] is None, "The deleted entry becomes None in entries."
    assert d[9] == "b", (
        "After deleting 1, key 9 (probe path 1 -> 2) must still be found. The tombstone in slot 1 must not "
        "end the search: only a None slot means 'absent'."
    )
    assert len(d) == 1 and list(d) == [9]


def test_new_key_reuses_tombstone():
    d = ToyDict()
    d[1] = "a"
    d[9] = "b"
    del d[1]
    d[17] = "c"
    assert d.indices[1] == 2, "A new key goes into the first FREE OR TOMBSTONE slot on its path (slot 1 here)."
    assert (d[9], d[17]) == ("b", "c")


def test_collisions_and_tombstones():
    d = ToyDict()
    a, b, c = Collide(1), Collide(2), Collide(3)
    d[a], d[b], d[c] = "A", "B", "C"
    assert (d[a], d[b], d[c]) == ("A", "B", "C"), "Equal hashes: compare keys with == after the hash matches."
    del d[b]
    assert d[c] == "C", "c sits after b's tombstone on the same probe path: keep probing past DELETED."
    assert d[Collide(3)] == "C", "A different but EQUAL key must find the entry (hash equal and == True)."
    assert Collide(4) not in d, "An absent colliding key: the search ends at a None slot."


def test_no_duplicate_key_after_tombstone():
    d = ToyDict()
    a, b = Collide(1), Collide(2)
    d[a] = "A"
    d[b] = "B"
    del d[a]
    d[b] = "B2"
    assert len(d) == 1 and d.items() == [(b, "B2")], (
        "b exists AFTER the tombstone. Look the key up fully before inserting; do not put a second b into "
        "the first tombstone you meet."
    )


def test_resize_at_two_thirds():
    d = ToyDict()
    capacities = []
    for k in range(1, 23):
        d[k] = k
        capacities.append(d.capacity)
    expected = [8] * 5 + [16] * 5 + [32] * 11 + [64]
    assert capacities == expected, (
        f"Capacities after each insert: {capacities}. Before adding a new key, resize when "
        "len(entries) + 1 > capacity * 2 // 3 (8 -> at most 5 entries, 16 -> 10, 32 -> 21)."
    )
    assert all(d[k] == k for k in range(1, 23)), "Every key must still be found after the resizes."


def test_resize_rebuilds_indices_without_tombstones():
    d = ToyDict()
    for k in range(5):
        d[k] = k
    for k in range(4):
        del d[k]
    d[100] = "new"
    assert d.capacity == 8, (
        "Only 1 live key + the new one: the smallest power of two >= 8 that fits is 8 again."
    )
    assert len(d.entries) == 2 and None not in d.entries, (
        "A resize keeps only the live entries; then the new entry is appended."
    )
    assert DELETED not in d.indices, "Indices are rebuilt from scratch: no tombstones survive a resize."
    assert list(d) == [4, 100] and d[4] == 4 and d[100] == "new"


def test_updates_never_resize():
    d = ToyDict()
    for k in range(5):
        d[k] = k
    for _ in range(10):
        for k in range(5):
            d[k] += 1
    assert d.capacity == 8 and len(d.entries) == 5, "Changing values of existing keys must not grow anything."


def test_iteration_order_and_items():
    d = ToyDict()
    for k in ["z", "a", "m"]:
        d[k] = k.upper()
    del d["a"]
    d["a"] = "again"
    assert list(d) == ["z", "m", "a"], "A key deleted and added again goes to the END (a new entry)."
    assert d.items() == [("z", "Z"), ("m", "M"), ("a", "again")], "items() returns (key, value) pairs in order."


def test_behaves_like_dict():
    rng = random.Random(24)
    real, toy = {}, ToyDict()
    for step in range(3000):
        key = rng.choice([rng.randrange(60), f"k{rng.randrange(60)}"])
        if rng.random() < 0.3 and key in real:
            del real[key]
            del toy[key]
        else:
            real[key] = step
            toy[key] = step
        assert len(toy) == len(real), f"Length differs after step {step}."
    assert list(toy) == list(real), "Iteration order must match a real dict (insertion order, deleted keys removed)."
    assert all(toy[k] == v for k, v in real.items()), "Every value must match a real dict."
    assert toy.capacity * 2 // 3 >= len(toy.entries), "The table may never be fuller than 2/3."


def test_unhashable_key():
    d = ToyDict()
    with pytest.raises(TypeError):
        d[[1, 2]] = "list"
