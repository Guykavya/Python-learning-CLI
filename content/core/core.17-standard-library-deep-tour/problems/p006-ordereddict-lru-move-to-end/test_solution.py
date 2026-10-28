import pytest

from solution import LRUCache


def test_example():
    c = LRUCache(2)
    c.put("a", 1)
    c.put("b", 2)
    assert c.get("a") == 1, "get returns the stored value."
    c.put("c", 3)
    assert c.keys() == ["a", "c"], "get('a') made 'a' the newest, so putting 'c' evicts 'b' (the least recently used)."
    assert c.get("b") is None, "'b' was evicted: get returns the default, None."


def test_put_and_len():
    c = LRUCache(3)
    assert len(c) == 0, "A new cache is empty."
    c.put(1, "x")
    c.put(2, "y")
    assert len(c) == 2, "Two puts, two entries."
    assert c.keys() == [1, 2], "keys() lists least recently used first."


def test_evicts_oldest_not_newest():
    c = LRUCache(2)
    c.put("a", 1)
    c.put("b", 2)
    c.put("c", 3)
    assert c.keys() == ["b", "c"], "Evict from the START: popitem(last=False). popitem() alone removes the newest."
    assert len(c) == 2, "Never hold more than capacity entries."


def test_get_refreshes():
    c = LRUCache(3)
    for k in "abc":
        c.put(k, k.upper())
    c.get("a")
    assert c.keys() == ["b", "c", "a"], "A hit must move the key to the end: move_to_end(key)."


def test_get_miss_changes_nothing():
    c = LRUCache(2)
    c.put("a", 1)
    c.put("b", 2)
    assert c.get("zzz") is None, "A miss returns the default."
    assert c.get("zzz", -1) == -1, "A miss returns the default you pass."
    assert c.keys() == ["a", "b"], "A miss must not add the key or reorder anything."
    assert len(c) == 2, "A miss must not store anything."


def test_put_existing_refreshes_and_overwrites():
    c = LRUCache(2)
    c.put("a", 1)
    c.put("b", 2)
    c.put("a", 10)
    assert c.keys() == ["b", "a"], (
        "Overwriting a key must also make it the newest. Assigning od[key] = v does NOT move an existing key: call move_to_end."
    )
    assert c.get("a") == 10, "The new value replaces the old one."
    c.put("c", 3)
    assert c.keys() == ["a", "c"], "Now 'b' is the least recently used and is evicted."


def test_overwrite_when_full_does_not_evict():
    c = LRUCache(2)
    c.put("a", 1)
    c.put("b", 2)
    c.put("b", 20)
    assert c.keys() == ["a", "b"], "Updating an existing key does not grow the cache, so nothing is evicted."


def test_falsy_values():
    c = LRUCache(2)
    c.put("zero", 0)
    c.put("none", None)
    assert c.get("zero", "missing") == 0, "0 is a stored value, not a miss: check 'key in data', not the truthiness of the value."
    assert c.get("none", "missing") is None, "None can be a stored value too."
    assert c.keys() == ["zero", "none"], "Both hits refreshed their keys in order."


def test_capacity_one():
    c = LRUCache(1)
    c.put("a", 1)
    c.put("b", 2)
    assert c.keys() == ["b"], "With capacity 1, every new key evicts the previous one."


def test_bad_capacity():
    with pytest.raises(ValueError):
        LRUCache(0)
    with pytest.raises(ValueError):
        LRUCache(-5)


def test_caches_are_separate():
    a = LRUCache(2)
    b = LRUCache(2)
    a.put("k", 1)
    assert b.get("k") is None, "Each cache needs its own OrderedDict: create it in __init__, not as a class attribute."
