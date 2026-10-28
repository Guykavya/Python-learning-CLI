# Project: a generic, fully typed LRU cache

Build a small library in `solution.py` that uses most of this module: a generic class with two
type variables, a `TypedDict` result, a callback type, a `ParamSpec` decorator, and **complete
annotations**. The goal is code that `python -m mypy --strict solution.py` accepts. The tests do
not run mypy: they read the hints at run time and check the behaviour.

An **LRU** (least recently used) cache holds at most `capacity` entries. When a new key would go
over the limit, the entry that was used **longest ago** is thrown out.

## Part 1: the types

```python
K = TypeVar("K")
V = TypeVar("V")

class CacheStats(TypedDict):
    hits: int
    misses: int
    evictions: int
    size: int
    capacity: int

class LRUCache(Generic[K, V]): ...      # or: class LRUCache[K, V]: ...
```

`K` is the key type, `V` the value type. `LRUCache[str, int]` is a cache of `str -> int`.

## Part 2: the methods

| Method | Hints | Behaviour |
|---|---|---|
| `__init__(capacity, on_evict=None)` | `capacity: int`, `on_evict: Callable[[K, V], None] \| None = None` -> `None` | `capacity < 1` raises `ValueError` |
| `capacity` (a `@property`) | -> `int` | the capacity |
| `get(key)` | `key: K` -> `V \| None` | the value, or `None` if absent. A **hit** or a **miss** is counted. A hit makes the key the most recently used |
| `__getitem__(key)` | `key: K` -> `V` | like `get` but raises `KeyError` when absent (a miss is counted) |
| `put(key, value)` | `key: K`, `value: V` -> `None` | inserts or updates, and makes the key the most recently used. If the cache is now over capacity, the least recently used entry is removed: that is one **eviction**, and `on_evict(key, value)` is called with the removed entry |
| `pop(key)` | `key: K` -> `V` | removes and returns the value; `KeyError` if absent. Not an eviction, no callback, no stats change |
| `peek(key)` | `key: K` -> `V \| None` | the value without changing the order or the stats |
| `keys()` | -> `list[K]` | all keys, **most recently used first** |
| `items()` | -> `list[tuple[K, V]]` | all `(key, value)` pairs, most recently used first |
| `clear()` | -> `None` | removes all entries (no callback). The counters keep their values |
| `stats()` | -> `CacheStats` | the counters: `hits`, `misses`, `evictions`, plus the current `size` and `capacity` |
| `__len__()` | -> `int` | number of entries |
| `__contains__(key)` | `key: object` -> `bool` | membership; changes neither the order nor the stats |

`get` must tell "key absent" from "key present with the value `None`": a cache of type
`LRUCache[str, int | None]` may legally store `None`, and finding it is still a **hit**.

## Part 3: the decorator

```python
def lru_memoize(capacity: int) -> Callable[[Callable[P, R]], Callable[P, R]]: ...
```

`@lru_memoize(2)` caches the results of a function in an `LRUCache` of that capacity. The cache
key is built from the call: `(args, tuple(sorted(kwargs.items())))`, so `f(1, b=2, a=3)` and
`f(1, a=3, b=2)` share an entry. A result of `None` must be cached too. Use `functools.wraps`.
The `ParamSpec` keeps the decorated function's signature. An unhashable argument raises
`TypeError` (the dictionary does that for you).

## Part 4: completeness (the "strict" part)

Every public function and method in the module (and `__init__`, `__len__`, ...) must annotate all
parameters except `self`, and the return. No `Any`. The tests check this with `inspect.signature`.

**Example**

```python
cache: LRUCache[str, int] = LRUCache(2)
cache.put("a", 1)
cache.put("b", 2)
cache.get("a")          # 1       ("a" is now the most recently used)
cache.put("c", 3)       # evicts "b"
cache.keys()            # ["c", "a"]
cache.stats()           # {"hits": 1, "misses": 0, "evictions": 1, "size": 2, "capacity": 2}

@lru_memoize(128)
def fib(n: int) -> int:
    return n if n < 2 else fib(n - 1) + fib(n - 2)
```

**Remember**: a dictionary keeps insertion order. If "most recently used" means "last in the
dict", then "use a key" means "remove it and add it again", and "least recently used" is
`next(iter(d))`.
