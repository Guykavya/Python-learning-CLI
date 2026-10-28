# OrderedDict: an LRU cache with move_to_end

A cache with limited room must throw something out when it is full. A good rule is **LRU,
least recently used**: throw out the entry that nobody has touched for the longest time.

Plain dicts keep insertion order too, but `collections.OrderedDict` has the two moves an LRU
needs, both O(1):

- `od.move_to_end(key)`: mark `key` as the newest.
- `od.popitem(last=False)`: remove and return the **oldest** `(key, value)`.

Write a class `LRUCache` in `solution.py`:

- `LRUCache(capacity: int)`: `capacity < 1` raises `ValueError`.
- `get(key, default=None)`: the value, or `default` if the key is missing. A hit makes the key the
  **most recently used**. A miss changes nothing.
- `put(key, value)`: store or overwrite; the key becomes the most recently used. If the cache is
  now over capacity, evict the least recently used entry.
- `__len__()`: the number of stored entries.
- `keys() -> list`: the keys from **least** to **most** recently used.

**Example**

```python
c = LRUCache(2)
c.put("a", 1)
c.put("b", 2)
c.get("a")        # 1   -> "a" is now the newest
c.put("c", 3)     # full: evicts "b", the least recently used
c.keys()          # ['a', 'c']
c.get("b")        # None
```
