import inspect
import typing
from collections.abc import Callable
from typing import Any, ParamSpec, TypeVar, get_args, get_origin, get_type_hints, is_typeddict

import pytest

import solution
from solution import CacheStats, LRUCache, lru_memoize


# =============================================================== Part 1: types and structure
def test_cache_stats_is_a_typeddict_of_ints():
    assert is_typeddict(CacheStats), "CacheStats must be a TypedDict."
    assert get_type_hints(CacheStats) == dict.fromkeys(("hits", "misses", "evictions", "size", "capacity"), int), (
        "CacheStats has the int keys hits, misses, evictions, size, capacity."
    )
    assert CacheStats.__required_keys__ == {"hits", "misses", "evictions", "size", "capacity"}, "All five keys are required."


def test_lru_cache_is_generic_in_k_and_v():
    params = getattr(LRUCache, "__parameters__", ())
    assert len(params) == 2 and all(isinstance(p, TypeVar) for p in params), (
        "LRUCache must be generic over two TypeVars: class LRUCache(Generic[K, V]) (or class LRUCache[K, V])."
    )
    assert params[0] is not params[1], "K and V are two different TypeVars."
    alias = LRUCache[str, int]
    assert get_args(alias) == (str, int), "LRUCache[str, int] must work (it needs Generic[K, V])."
    c = LRUCache[str, int](2)
    c.put("a", 1)
    assert c.get("a") == 1, "A subscripted class can be called like the plain class."


def test_method_hints_use_the_class_typevars():
    k, v = LRUCache.__parameters__
    h = get_type_hints(LRUCache.get)
    assert h["key"] is k, "get(key: K): the key type is the class's first TypeVar."
    assert h["return"] == v | None, "get returns V | None."
    assert get_type_hints(LRUCache.__getitem__) == {"key": k, "return": v}, "__getitem__(key: K) -> V."
    assert get_type_hints(LRUCache.put) == {"key": k, "value": v, "return": type(None)}, "put(key: K, value: V) -> None."
    assert get_type_hints(LRUCache.pop) == {"key": k, "return": v}, "pop(key: K) -> V."
    assert get_type_hints(LRUCache.peek) == {"key": k, "return": v | None}, "peek(key: K) -> V | None."
    assert get_type_hints(LRUCache.keys)["return"] == list[k], "keys() -> list[K]."
    assert get_type_hints(LRUCache.items)["return"] == list[tuple[k, v]], "items() -> list[tuple[K, V]]."


def test_other_hints():
    k, v = LRUCache.__parameters__
    h = get_type_hints(LRUCache.__init__)
    assert h["capacity"] is int and h["return"] is type(None), "__init__(capacity: int, ...) -> None."
    assert h["on_evict"] == Callable[[k, v], None] | None, "on_evict: Callable[[K, V], None] | None = None."
    assert inspect.signature(LRUCache.__init__).parameters["on_evict"].default is None, "on_evict defaults to None."
    assert isinstance(inspect.getattr_static(LRUCache, "capacity"), property), "capacity must be a @property."
    assert get_type_hints(LRUCache.capacity.fget)["return"] is int, "The capacity property returns int."
    assert get_type_hints(LRUCache.stats)["return"] is CacheStats, "stats() -> CacheStats."
    assert get_type_hints(LRUCache.clear)["return"] is type(None), "clear() -> None."
    assert get_type_hints(LRUCache.__len__)["return"] is int, "__len__ -> int."
    assert get_type_hints(LRUCache.__contains__) == {"key": object, "return": bool}, (
        "__contains__(key: object) -> bool: it accepts any object, because 'x in cache' may test any type."
    )


def test_lru_memoize_hints():
    h = get_type_hints(lru_memoize)
    assert h["capacity"] is int, "lru_memoize(capacity: int)."
    ret = h["return"]
    assert get_origin(ret) is get_origin(Callable[[int], int]), "lru_memoize returns a decorator: Callable[[Callable[P, R]], Callable[P, R]]."
    (params, inner) = get_args(ret)
    assert len(params) == 1 and get_args(params[0]) == get_args(inner), "The decorator takes Callable[P, R] and returns the same Callable[P, R]."
    p, r = get_args(inner)
    assert isinstance(p, ParamSpec) and isinstance(r, TypeVar), "Use a ParamSpec P and a TypeVar R."


# =============================================================== Part 2: behaviour
def test_capacity_validation_and_property():
    with pytest.raises(ValueError):
        LRUCache(0)
    with pytest.raises(ValueError):
        LRUCache(-3)
    assert LRUCache(5).capacity == 5, "The capacity property returns the capacity."
    assert LRUCache(1).capacity == 1, "Capacity 1 is allowed."


def test_put_and_get():
    c = LRUCache(2)
    c.put("a", 1)
    assert c.get("a") == 1, "get returns what put stored."
    assert c.get("zzz") is None, "Absent key: None."
    c.put("a", 10)
    assert c.get("a") == 10 and len(c) == 1, "put on an existing key updates the value and does not grow the cache."


def test_eviction_removes_least_recently_used():
    c = LRUCache(2)
    c.put("a", 1)
    c.put("b", 2)
    c.put("c", 3)
    assert "a" not in c and "b" in c and "c" in c, "'a' is the oldest: it must be evicted when 'c' arrives."
    assert len(c) == 2, "The cache never holds more than capacity entries."


def test_get_refreshes_recency():
    c = LRUCache(2)
    c.put("a", 1)
    c.put("b", 2)
    c.get("a")
    c.put("c", 3)
    assert c.keys() == ["c", "a"], "get('a') made 'a' recent, so 'b' was the least recently used and is evicted."


def test_put_update_refreshes_recency_and_never_evicts():
    c = LRUCache(2)
    c.put("a", 1)
    c.put("b", 2)
    c.put("a", 11)
    assert c.keys() == ["a", "b"], "Updating an existing key makes it the most recent."
    assert c.stats()["evictions"] == 0, "Updating a key does not evict anything, even when the cache is full."
    c.put("c", 3)
    assert c.keys() == ["c", "a"], "Now 'b' is the least recently used."


def test_capacity_one():
    c = LRUCache(1)
    c.put("a", 1)
    c.put("b", 2)
    assert c.keys() == ["b"], "With capacity 1 each put evicts the previous key."
    assert c.get("a") is None, "'a' is gone."


def test_none_value_is_a_hit_not_a_miss():
    c = LRUCache(2)
    c.put("a", None)
    assert c.get("a") is None, "The stored value is None."
    assert c.stats()["hits"] == 1 and c.stats()["misses"] == 0, (
        "A stored None is a HIT. Do not test 'if value is None' to detect a miss: test 'key in data'."
    )
    c.get("b")
    assert c.stats()["misses"] == 1, "An absent key is a miss."


def test_getitem():
    c = LRUCache(2)
    c.put("a", 1)
    c.put("b", 2)
    assert c["a"] == 1, "c[key] returns the value."
    with pytest.raises(KeyError):
        c["zzz"]
    assert c.keys() == ["a", "b"], "c['a'] refreshes recency, like get."
    s = c.stats()
    assert (s["hits"], s["misses"]) == (1, 1), "c[key] counts a hit; a failed c[key] counts a miss."


def test_peek_and_contains_do_not_touch_order_or_stats():
    c = LRUCache(2)
    c.put("a", 1)
    c.put("b", 2)
    assert c.peek("a") == 1 and c.peek("zzz") is None, "peek returns the value or None."
    assert "a" in c and "zzz" not in c, "in works."
    assert c.keys() == ["b", "a"], "peek and 'in' must NOT change the order."
    s = c.stats()
    assert (s["hits"], s["misses"]) == (0, 0), "peek and 'in' must NOT count hits or misses."
    c.put("c", 3)
    assert "a" not in c, "'a' was never refreshed, so it is the one evicted."


def test_keys_and_items_most_recent_first():
    c = LRUCache(3)
    for i, k in enumerate("abc", 1):
        c.put(k, i)
    assert c.keys() == ["c", "b", "a"], "keys() lists the most recently used first."
    assert c.items() == [("c", 3), ("b", 2), ("a", 1)], "items() lists (key, value) pairs, most recent first."
    c.get("a")
    assert c.keys() == ["a", "c", "b"], "After get('a'), 'a' is first."
    keys = c.keys()
    keys.clear()
    assert len(c) == 3, "keys() returns a new list; changing it must not change the cache."


def test_pop():
    c = LRUCache(3)
    c.put("a", 1)
    c.put("b", 2)
    assert c.pop("a") == 1, "pop returns the value."
    assert "a" not in c and len(c) == 1, "pop removes the entry."
    with pytest.raises(KeyError):
        c.pop("a")
    s = c.stats()
    assert (s["hits"], s["misses"], s["evictions"]) == (0, 0, 0), "pop changes no counter (it is not a hit, a miss or an eviction)."


def test_clear_keeps_counters():
    c = LRUCache(2)
    c.put("a", 1)
    c.get("a")
    c.get("x")
    c.clear()
    assert len(c) == 0 and c.keys() == [], "clear removes everything."
    s = c.stats()
    assert (s["hits"], s["misses"], s["size"], s["capacity"]) == (1, 1, 0, 2), "clear keeps the counters; size is 0."
    c.put("b", 2)
    assert c.get("b") == 2, "The cache still works after clear."


def test_stats():
    c = LRUCache(2)
    assert c.stats() == {"hits": 0, "misses": 0, "evictions": 0, "size": 0, "capacity": 2}, "A new cache: all zeros, capacity 2."
    c.put("a", 1)
    c.put("b", 2)
    c.get("a")
    c.get("zzz")
    c.put("c", 3)
    assert c.stats() == {"hits": 1, "misses": 1, "evictions": 1, "size": 2, "capacity": 2}, (
        "1 hit (a), 1 miss (zzz), 1 eviction (b), size 2."
    )
    snapshot = c.stats()
    c.get("a")
    assert snapshot["hits"] == 1, "stats() returns a new dict each time (a snapshot)."


def test_len_and_unhashable_key():
    c = LRUCache(3)
    assert len(c) == 0, "Empty cache has length 0."
    c.put(1, "x")
    c.put((1, 2), "y")
    assert len(c) == 2, "len counts the entries (keys can be any hashable value)."
    with pytest.raises(TypeError):
        c.put([1], "bad")


# =============================================================== Part 3: on_evict callback
def test_on_evict_called_with_key_and_value():
    log = []
    c = LRUCache(2, on_evict=lambda k, v: log.append((k, v)))
    c.put("a", 1)
    c.put("b", 2)
    assert log == [], "No eviction yet: no callback."
    c.put("c", 3)
    assert log == [("a", 1)], "The callback receives the evicted key and value."
    c.get("b")
    c.put("d", 4)
    assert log == [("a", 1), ("c", 3)], "'b' was refreshed, so 'c' was evicted next."


def test_on_evict_not_called_for_update_pop_clear():
    log = []
    c = LRUCache(2, on_evict=lambda k, v: log.append((k, v)))
    c.put("a", 1)
    c.put("a", 2)
    c.put("b", 3)
    c.pop("b")
    c.clear()
    assert log == [], "The callback is only for evictions caused by put(): not for updates, pop or clear."
    assert c.stats()["evictions"] == 0, "And none of those count as evictions."


def test_on_evict_sees_the_cache_already_updated():
    seen = []
    holder = []
    c = LRUCache(1, on_evict=lambda k, v: seen.append((k, "a" in holder[0], len(holder[0]))))
    holder.append(c)
    c.put("a", 1)
    c.put("b", 2)
    assert seen == [("a", False, 1)], "When the callback runs, the old entry is already removed and the new one is in."


# =============================================================== Part 4: lru_memoize
def test_memoize_caches_results():
    calls = []

    @lru_memoize(3)
    def square(n):
        calls.append(n)
        return n * n

    assert square(4) == 16 and square(4) == 16 and square(5) == 25, "Results are returned correctly."
    assert calls == [4, 5], "The second square(4) must come from the cache."


def test_memoize_evicts_least_recently_used():
    calls = []

    @lru_memoize(2)
    def f(x):
        calls.append(x)
        return x

    f(1)
    f(2)
    f(1)
    f(3)
    f(2)
    assert calls == [1, 2, 3, 2], "f(3) evicted 2 (1 was used more recently), so f(2) is computed again."


def test_memoize_kwargs_order_and_positional_difference():
    calls = []

    @lru_memoize(5)
    def f(*args, **kwargs):
        calls.append((args, kwargs))
        return len(calls)

    a = f(1, b=2, a=3)
    b = f(1, a=3, b=2)
    assert a == b and len(calls) == 1, "Keyword argument order must not matter: sort the keyword items for the key."
    f(1, 2)
    f(1, b=2)
    assert len(calls) == 3, "Different arguments are different cache keys."


def test_memoize_caches_none_results():
    calls = []

    @lru_memoize(2)
    def f(x):
        calls.append(x)

    assert f(1) is None and f(1) is None, "None is returned."
    assert calls == [1], "A result of None is a real result and must be cached too."


def test_memoize_preserves_metadata():
    @lru_memoize(2)
    def area(width: int, height: int = 2) -> int:
        """Rectangle area."""
        return width * height

    assert area.__name__ == "area" and area.__doc__ == "Rectangle area.", "Use functools.wraps."
    assert str(inspect.signature(area)) == "(width: int, height: int = 2) -> int", "The signature must stay visible."


def test_memoize_unhashable_argument():
    @lru_memoize(2)
    def f(x):
        return x

    with pytest.raises(TypeError):
        f([1, 2])


def test_memoize_separate_caches_per_function():
    @lru_memoize(2)
    def f(x):
        return ("f", x)

    @lru_memoize(2)
    def g(x):
        return ("g", x)

    assert f(1) == ("f", 1) and g(1) == ("g", 1), "Each decorated function has its own cache."


def test_memoize_exceptions_not_cached():
    calls = []

    @lru_memoize(2)
    def f(x):
        calls.append(x)
        raise RuntimeError("no")

    for _ in range(2):
        with pytest.raises(RuntimeError):
            f(1)
    assert calls == [1, 1], "A call that raises has no result to cache."


def test_memoize_fib():
    @lru_memoize(64)
    def fib(n):
        return n if n < 2 else fib(n - 1) + fib(n - 2)

    assert fib(60) == 1548008755920, "With a cache this recursion is fast (without it, fib(60) never finishes)."


# =============================================================== Part 5: strict-style completeness
def own_callables():
    """Yield (qualified name, function) for every public function and method defined in solution."""
    for name, obj in vars(solution).items():
        if name.startswith("_") or getattr(obj, "__module__", None) != "solution":
            continue
        if inspect.isfunction(obj):
            yield name, obj
        elif inspect.isclass(obj) and not is_typeddict(obj):
            for mname, member in vars(obj).items():
                if mname.startswith("_") and not (mname.startswith("__") and mname.endswith("__")):
                    continue
                if mname in ("__module__", "__doc__", "__dict__", "__weakref__", "__qualname__", "__firstlineno__",
                             "__static_attributes__", "__orig_bases__", "__parameters__", "__annotations__",
                             "__annotate__", "__annotations_cache__", "__type_params__", "__slots__",
                             "__classdictcell__", "__abstractmethods__", "_abc_impl", "__protocol_attrs__"):
                    continue
                if isinstance(member, property):
                    for acc in (member.fget, member.fset, member.fdel):
                        if acc is not None:
                            yield f"{name}.{mname}", acc
                elif isinstance(member, (staticmethod, classmethod)):
                    yield f"{name}.{mname}", member.__func__
                elif inspect.isfunction(member):
                    yield f"{name}.{mname}", member


def test_every_public_function_and_method_is_fully_annotated():
    seen = [qual for qual, _ in own_callables()]
    for needed in ("lru_memoize", "LRUCache.__init__", "LRUCache.get", "LRUCache.put", "LRUCache.stats", "LRUCache.capacity"):
        assert needed in seen, f"{needed} was not found. Define it at module level / in the class."
    for qual, func in own_callables():
        sig = inspect.signature(func)
        for pname, p in sig.parameters.items():
            if pname in ("self", "cls"):
                continue
            assert p.annotation is not inspect.Parameter.empty, (
                f"{qual}: parameter '{pname}' has no annotation. In a strict module every parameter is annotated."
            )
        assert sig.return_annotation is not inspect.Signature.empty, (
            f"{qual} has no return annotation. Add '-> ...' (use '-> None' for functions that return nothing)."
        )


def _has_any(t):
    if t is Any:
        return True
    if isinstance(t, (list, tuple)):
        return any(_has_any(x) for x in t)
    return any(_has_any(a) for a in get_args(t))


def test_no_any_in_the_hints():
    for qual, func in own_callables():
        for name, hint in get_type_hints(func).items():
            assert not _has_any(hint), f"{qual}: '{name}' uses Any. In this project every type is precise."


def test_private_state_is_not_a_public_attribute():
    c = LRUCache(2)
    public = [n for n in vars(c) if not n.startswith("_")]
    assert public == [], (
        f"Public attributes found on an instance: {public}. Keep the data private (_data, _hits, ...) "
        "so callers use get/put/stats."
    )
