# A generic in-memory Repository

Many programs have a "store" class: users by id, products by sku, sessions by token. The code
is always the same; only the key type and the value type change. Write it once, generic in
the **key** `K` and the **value** `V`.

Write `class Repository` in `solution.py`, generic in `K` and `V` (in this order). Use
`Generic[K, V]` with two `TypeVar`s, or the new `class Repository[K, V]` syntax. It keeps a
dict inside. Methods and hints:

- `add(self, key: K, value: V) -> None`: store the value. If the key already exists, raise
  `KeyError(key)` and do not change anything.
- `get(self, key: K) -> V | None`: the value, or `None` if the key is missing.
- `require(self, key: K) -> V`: the value; raise `KeyError(key)` if missing.
- `remove(self, key: K) -> V`: delete the key and return its value; `KeyError(key)` if missing.
- `find(self, predicate: Callable[[V], bool]) -> list[V]`: all values for which `predicate` is
  `True`, in the order they were added.
- `all(self) -> list[V]`: all values in insertion order (a new list).
- `__len__(self) -> int`
- `__contains__(self, key: K) -> bool`

Import `Callable` from `collections.abc`. The tests check that every hint uses **the class's own**
type variables `K` and `V`, in the right places.

**Example**

```python
users: Repository[int, str] = Repository()
users.add(1, "ana")
users.add(2, "ben")
users.get(1)                     # 'ana'   a type checker says: str | None
users.require(2)                 # 'ben'   a type checker says: str
users.find(lambda n: "a" in n)   # ['ana']
users.get(9)                     # None
users.add(1, "again")            # KeyError: 1
```
