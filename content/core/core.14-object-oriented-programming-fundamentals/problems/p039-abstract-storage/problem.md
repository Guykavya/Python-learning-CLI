# An abstract storage and two backends

An app saves small key/value data. Today it keeps it in memory; later it may use a file or a
database. The rest of the app should only know **one interface**. Write an abstract base class
that defines that interface and two real storages in `solution.py`.

**`Storage(ABC)`** has four **abstract** methods that every real storage must write:

- `get(key)`: return the value, or raise `KeyError` if the key is missing.
- `set(key, value)`: store the value (replacing an old one).
- `delete(key)`: remove the key, or raise `KeyError` if it is missing.
- `keys()`: return a list of all keys.

It also has these **concrete** methods, written once in `Storage` using only the four above
(so every storage gets them for free):

- `get_or(key, default=None)`: the value, or `default` if the key is missing.
- `contains(key)`: `True` or `False`.
- `pop(key)`: return the value and delete the key; a missing key raises `KeyError`.
- `items()`: a list of `(key, value)` pairs **sorted by key**.
- `update(pairs)`: `set` every key/value of the dict `pairs`.
- `count()`: the number of keys.

`Storage()` itself must raise `TypeError` (Python does that for a class with abstract methods), and
so must a subclass that forgets one of the four.

**`MemoryStorage(initial=None)`**: keeps the data in a dict. `initial` is an optional dict of
starting data; keep your own copy. `keys()` gives the keys in insertion order.

**`PrefixStorage(inner, prefix)`**: lets several parts of the app share one storage without
clashing keys. It **wraps** another storage (it has one; it is not one of its kind):

- `inner` must be a `Storage`, otherwise `TypeError`. `prefix` must be a non-empty `str`,
  otherwise `ValueError`.
- `set("name", v)` stores `v` in `inner` under `prefix + "name"`; `get` and `delete` work the same
  way. A missing key raises `KeyError` with the key **without** the prefix.
- `keys()` returns only the inner keys that start with the prefix, with the prefix removed, in the
  inner storage's order.

**Example**

```python
db = MemoryStorage({"theme": "dark"})
users = PrefixStorage(db, "user:")
users.set("asha", 21)
users.update({"ravi": 19})
db.keys()               # ['theme', 'user:asha', 'user:ravi']
users.keys()            # ['asha', 'ravi']
users.items()           # [('asha', 21), ('ravi', 19)]
users.get_or("zoya", 0) # 0
users.pop("asha")       # 21
db.contains("user:asha")    # False
Storage()               # TypeError: Can't instantiate abstract class Storage ...
```
