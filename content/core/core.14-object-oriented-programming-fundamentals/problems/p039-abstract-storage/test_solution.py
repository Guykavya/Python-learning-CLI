import inspect

import pytest

from solution import MemoryStorage, PrefixStorage, Storage


class ListStorage(Storage):
    """A storage the solution has never seen: pairs in a list."""

    def __init__(self):
        self.pairs = []

    def get(self, key):
        for k, v in self.pairs:
            if k == key:
                return v
        raise KeyError(key)

    def set(self, key, value):
        self.pairs = [(k, v) for k, v in self.pairs if k != key] + [(key, value)]

    def delete(self, key):
        self.get(key)
        self.pairs = [(k, v) for k, v in self.pairs if k != key]

    def keys(self):
        return [k for k, _ in self.pairs]


def test_storage_is_abstract():
    assert inspect.isabstract(Storage), "Storage must have abstract methods (use @abstractmethod and inherit from ABC)."
    assert sorted(Storage.__abstractmethods__) == ["delete", "get", "keys", "set"], (
        "Exactly get, set, delete and keys are abstract. The other methods are concrete."
    )
    with pytest.raises(TypeError):
        Storage()


def test_incomplete_subclass_cannot_be_created():
    class NoKeys(Storage):
        def get(self, key):
            return 1

        def set(self, key, value):
            pass

        def delete(self, key):
            pass

    with pytest.raises(TypeError):
        NoKeys()


def test_memory_basics():
    db = MemoryStorage()
    db.set("a", 1)
    db.set("b", 2)
    db.set("a", 10)
    assert db.get("a") == 10, "set replaces an old value."
    assert db.keys() == ["a", "b"], "keys() in insertion order."
    db.delete("a")
    assert db.keys() == ["b"], "delete removes the key."
    with pytest.raises(KeyError):
        db.get("a")
    with pytest.raises(KeyError):
        db.delete("a")


def test_memory_initial_is_copied():
    start = {"theme": "dark"}
    db = MemoryStorage(start)
    db.set("x", 1)
    assert start == {"theme": "dark"}, "Keep your own copy of initial; do not change the caller's dict."
    assert MemoryStorage().keys() == [], "Without initial, the storage starts empty."
    a, b = MemoryStorage(), MemoryStorage()
    a.set("k", 1)
    assert b.keys() == [], "Two storages must not share data. Do not use initial={} as a default."


def test_concrete_methods_on_memory():
    db = MemoryStorage({"b": 2, "a": 1})
    assert db.get_or("a") == 1 and db.get_or("zz") is None and db.get_or("zz", 0) == 0, "get_or returns the default for a missing key."
    assert db.contains("a") is True and db.contains("zz") is False, "contains returns True or False."
    assert db.items() == [("a", 1), ("b", 2)], "items() is sorted by key."
    assert db.count() == 2, "count() is the number of keys."
    db.update({"c": 3, "a": 100})
    assert db.items() == [("a", 100), ("b", 2), ("c", 3)], "update sets every pair."
    assert db.pop("b") == 2, "pop returns the value."
    assert db.contains("b") is False, "pop also deletes the key."
    with pytest.raises(KeyError):
        db.pop("b")


def test_contains_with_falsy_values():
    db = MemoryStorage({"zero": 0, "none": None, "empty": ""})
    for key in ("zero", "none", "empty"):
        assert db.contains(key) is True, (
            f"contains({key!r}) must be True: the key exists even though its value is falsy. "
            "Catch KeyError instead of testing the value."
        )


def test_concrete_methods_work_for_any_subclass():
    s = ListStorage()
    s.update({"y": 2, "x": 1})
    assert s.items() == [("x", 1), ("y", 2)], (
        "The concrete methods must use only get/set/delete/keys, so they work for every subclass."
    )
    assert s.get_or("nope", "d") == "d" and s.count() == 2
    assert s.pop("x") == 1 and s.keys() == ["y"]


def test_prefix_storage():
    db = MemoryStorage({"theme": "dark"})
    users = PrefixStorage(db, "user:")
    users.set("asha", 21)
    users.update({"ravi": 19})
    assert db.keys() == ["theme", "user:asha", "user:ravi"], "PrefixStorage stores in the inner storage under prefix + key."
    assert users.keys() == ["asha", "ravi"], "keys() shows only keys with the prefix, with the prefix removed."
    assert users.get("asha") == 21, "get reads prefix + key from the inner storage."
    assert users.items() == [("asha", 21), ("ravi", 19)], "The concrete methods work through the prefix."
    assert users.get_or("zoya", 0) == 0, "get_or works through the prefix."
    assert users.pop("asha") == 21, "pop works through the prefix."
    assert db.contains("user:asha") is False, "pop deleted the prefixed key in the inner storage."
    assert users.count() == 1, "Only ravi is left under the prefix."


def test_prefix_storage_is_a_storage_and_wraps():
    db = MemoryStorage()
    p = PrefixStorage(db, "a:")
    assert isinstance(p, Storage), "PrefixStorage must be a Storage subclass, so it offers the same interface."
    nested = PrefixStorage(p, "b:")
    nested.set("k", 1)
    assert db.keys() == ["a:b:k"], "A PrefixStorage can wrap another PrefixStorage (it only needs a Storage)."


def test_prefix_missing_key_error():
    users = PrefixStorage(MemoryStorage(), "user:")
    with pytest.raises(KeyError) as info:
        users.get("zoya")
    assert info.value.args == ("zoya",), "The KeyError should name the key without the prefix: KeyError('zoya')."
    with pytest.raises(KeyError) as info:
        users.delete("zoya")
    assert info.value.args == ("zoya",), "delete of a missing key: KeyError('zoya'), without the prefix."


def test_prefix_keeps_others_apart():
    db = MemoryStorage()
    users = PrefixStorage(db, "user:")
    carts = PrefixStorage(db, "cart:")
    users.set("1", "asha")
    carts.set("1", ["pen"])
    assert users.get("1") == "asha" and carts.get("1") == ["pen"], "The same short key under two prefixes must not clash."
    assert users.keys() == ["1"] and carts.keys() == ["1"], "Each prefix sees only its own keys."


def test_prefix_bad_arguments():
    with pytest.raises(TypeError):
        PrefixStorage({"a": 1}, "x:")
    with pytest.raises(ValueError):
        PrefixStorage(MemoryStorage(), "")
    with pytest.raises(ValueError):
        PrefixStorage(MemoryStorage(), 5)
