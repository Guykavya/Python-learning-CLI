from collections.abc import Callable
from typing import TypeVar, get_args, get_origin, get_type_hints

import pytest

from solution import Repository


def kv():
    ps = getattr(Repository, "__parameters__", ())
    assert len(ps) == 2 and all(isinstance(p, TypeVar) for p in ps), (
        "Repository must be generic in two TypeVars, in this order: class Repository(Generic[K, V]) (key first, value second)."
    )
    return ps


def test_two_type_parameters():
    k, v = kv()
    assert k is not v, "K and V must be two different TypeVars."


def test_key_and_value_hints():
    k, v = kv()
    assert get_type_hints(Repository.add) == {"key": k, "value": v, "return": type(None)}, "add(self, key: K, value: V) -> None."
    assert get_type_hints(Repository.require) == {"key": k, "return": v}, "require(self, key: K) -> V."
    assert get_type_hints(Repository.remove) == {"key": k, "return": v}, "remove(self, key: K) -> V."
    assert get_type_hints(Repository.__contains__) == {"key": k, "return": bool}, "__contains__(self, key: K) -> bool."
    assert get_type_hints(Repository.__len__) == {"return": int}, "__len__ -> int."


def test_get_may_return_none():
    k, v = kv()
    h = get_type_hints(Repository.get)
    assert h["key"] is k, "get(self, key: K)."
    assert set(get_args(h["return"])) == {v, type(None)}, "get returns the value or None: -> V | None."


def test_find_and_all_hints():
    k, v = kv()
    h = get_type_hints(Repository.find)
    pred = h["predicate"]
    assert get_origin(pred) is get_origin(Callable[[int], bool]), "predicate: Callable[[V], bool]."
    (args, ret) = get_args(pred)
    assert list(args) == [v] and ret is bool, "predicate takes ONE value (type V) and returns bool: Callable[[V], bool]."
    assert h["return"] == list[v], "find returns list[V]."
    assert get_type_hints(Repository.all) == {"return": list[v]}, "all returns list[V]."


def test_add_get_require():
    r = Repository()
    r.add(1, "ana")
    r.add(2, "ben")
    assert r.get(1) == "ana" and r.require(2) == "ben", "get and require return the stored value."
    assert r.get(9) is None, "get on a missing key gives None."
    with pytest.raises(KeyError):
        r.require(9)


def test_none_and_falsy_values_are_stored():
    r = Repository()
    r.add("k", 0)
    assert r.get("k") == 0 and "k" in r, "0 is a stored value, not 'missing'."
    r.add("n", None)
    assert "n" in r and r.require("n") is None, "None may be stored as a value; require must not raise for it."


def test_duplicate_key_rejected():
    r = Repository()
    r.add(1, "ana")
    with pytest.raises(KeyError):
        r.add(1, "again")
    assert r.require(1) == "ana", "A rejected add must not overwrite the old value."
    assert len(r) == 1, "A rejected add must not change the size."


def test_remove():
    r = Repository()
    r.add(1, "ana")
    assert r.remove(1) == "ana", "remove returns the removed value."
    assert 1 not in r and len(r) == 0, "The key is gone."
    with pytest.raises(KeyError):
        r.remove(1)


def test_find_and_all_keep_insertion_order():
    r = Repository()
    for i, name in enumerate(["ana", "ben", "cara", "bo"]):
        r.add(i, name)
    assert r.find(lambda n: n.startswith("b")) == ["ben", "bo"], "find keeps the order the values were added."
    assert r.find(lambda n: False) == [], "Nothing matches: empty list."
    assert r.all() == ["ana", "ben", "cara", "bo"], "all() lists every value in insertion order."


def test_all_returns_a_copy():
    r = Repository()
    r.add(1, "a")
    out = r.all()
    out.append("zzz")
    assert r.all() == ["a"], "all() must return a new list; changing it must not change the repository."


def test_len_and_contains():
    r = Repository()
    assert len(r) == 0 and 1 not in r, "A new repository is empty."
    r.add(1, "a")
    assert len(r) == 1 and 1 in r, "One entry."


def test_independent_instances_and_subscripting():
    a, b = Repository(), Repository[int, str]()
    a.add(1, "x")
    assert len(b) == 0, "Each repository needs its own dict, created in __init__."
    assert get_origin(Repository[int, str]) is Repository, "Repository[int, str] must be allowed."
