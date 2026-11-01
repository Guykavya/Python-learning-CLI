# A cache that does not keep objects alive

A normal dict cache keeps every value alive forever, because the dict holds a strong reference.
Sometimes you want "share the object while somebody is using it, forget it when nobody is".
`weakref.WeakValueDictionary` does exactly that: it holds its values through **weak
references**, and an entry disappears by itself as soon as its value has no strong references
left.

```python
import weakref
d = weakref.WeakValueDictionary()
img = Image("cat.png")
d["cat"] = img
"cat" in d      # True
del img         # the last strong reference is gone
"cat" in d      # False (the entry vanished)
```

Only objects that support weak references can be stored: instances of your own classes can,
but `int`, `str`, `tuple` and `list` cannot (storing one raises `TypeError`).

Copy `starter.py` to `solution.py` and write the class **`Cache(factory)`**:

- `get(key)` returns the cached object for `key` if it is still alive (a **hit**); otherwise it
  calls `factory(key)`, stores the new object and returns it (a **miss**).
- `hits` and `misses` are attributes counting both cases, starting at 0.
- `len(cache)` is the number of entries whose object is still alive.
- `key in cache` is `True` only while that key's object is alive.

**Example**

```python
class Image:
    def __init__(self, name):
        self.name = name

cache = Cache(Image)
a = cache.get("cat.png")      # miss: Image("cat.png") is created
b = cache.get("cat.png")      # hit: the same object
a is b                        # True
cache.hits, cache.misses      # (1, 1)
del a, b                      # nobody uses it any more
"cat.png" in cache            # False
c = cache.get("cat.png")      # miss again: a new Image
cache.misses                  # 2
```

In CPython the entry vanishes right at `del`, thanks to reference counting. Other Pythons free
objects later, which is why the tests call `gc.collect()` before checking.
