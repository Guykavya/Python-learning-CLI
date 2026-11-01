import gc
import weakref

import pytest

from solution import Cache


class Image:
    def __init__(self, name):
        self.name = name


def test_miss_then_hit_shares_the_object():
    cache = Cache(Image)
    a = cache.get("cat.png")
    b = cache.get("cat.png")
    assert isinstance(a, Image) and a.name == "cat.png", "On a miss, return factory(key)."
    assert a is b, "While the first object is alive, get must return the SAME object (a hit)."
    assert (cache.hits, cache.misses) == (1, 1), "One miss (first get) and one hit (second get)."


def test_different_keys_are_different_objects():
    cache = Cache(Image)
    a = cache.get("a")
    b = cache.get("b")
    assert a is not b and (a.name, b.name) == ("a", "b"), "Each key gets its own object."
    assert len(cache) == 2, "Two live objects means two entries."
    assert "a" in cache and "b" in cache, "Keys of live objects are in the cache."


def test_entry_vanishes_when_unused():
    cache = Cache(Image)
    a = cache.get("cat.png")
    probe = weakref.ref(a)
    del a
    gc.collect()
    assert probe() is None, (
        "The cache kept the object alive. Store values in a weakref.WeakValueDictionary, not a normal dict."
    )
    assert "cat.png" not in cache, "Once the object is gone its key must not be in the cache."
    assert len(cache) == 0, "len counts only live entries."


def test_recreated_after_vanishing():
    cache = Cache(Image)
    first = cache.get("x")
    del first
    gc.collect()
    again = cache.get("x")
    assert isinstance(again, Image) and again.name == "x", "After the old object died, get must create a new one."
    assert (cache.hits, cache.misses) == (0, 2), "Both gets were misses: the first object had died in between."


def test_alive_object_keeps_its_entry():
    cache = Cache(Image)
    keep = cache.get("keep")
    gone = cache.get("gone")
    del gone
    gc.collect()
    assert "keep" in cache and "gone" not in cache, "Only the entry whose object died disappears."
    assert cache.get("keep") is keep, "An object still in use must be returned again (a hit)."
    assert len(cache) == 1, "One live entry left."


def test_factory_called_once_per_miss():
    calls = []

    def factory(key):
        calls.append(key)
        return Image(key)

    cache = Cache(factory)
    held = [cache.get("k") for _ in range(5)]
    assert calls == ["k"], "factory must run only on a miss; four of the five gets were hits."
    assert all(h is held[0] for h in held), "Every hit returns the same object."


def test_get_returns_a_strong_reference():
    cache = Cache(Image)
    obj = cache.get("fresh")
    assert obj is not None and obj.name == "fresh", (
        "Return the object you created (a strong reference). Re-reading it from the WeakValueDictionary "
        "after storing can find it already gone."
    )


def test_values_must_support_weak_references():
    cache = Cache(len)
    with pytest.raises(TypeError):
        cache.get("abc")
