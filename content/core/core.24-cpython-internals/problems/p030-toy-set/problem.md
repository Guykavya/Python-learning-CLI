# Build a hash set: open addressing, tombstones and resizing

CPython's `set` is a hash table with **open addressing**: one array of slots, and every item
lives directly in a slot (no linked lists). To find an item, compute `hash(item)`, pick a starting
slot from it, and **probe** slot after slot until you find the item or an empty slot. Build a
smaller version, `ToySet`, with **linear probing** (the next slot is `index + 1`, wrapping around).

Copy `starter.py` to `solution.py`. The table is already set up: `self._slots` is a list of
`capacity` slots (starting at 8), and each slot is `None` (never used), `_DELETED` (a
tombstone), or a tuple `(hash, item)`. `self._used` counts live items and `self._fill` counts
live items **plus** tombstones.

**Probing.** Start at `hash(item) & (capacity - 1)` (capacity is a power of two, so this is
`hash % capacity`, also for negative hashes). A slot matches when its stored hash equals the hash
you look for **and** (`stored is item` or `stored == item`), the same test CPython uses: the hash
comparison is cheap and avoids calling `==` on items that cannot be equal, and the `is` check
makes `float("nan")` findable. Stop at the first `None` slot: the item is not there.

**Tombstones.** `remove` cannot put `None` back into a slot: a later item that probed past this
slot would then become unreachable. Put `_DELETED` there instead. Lookups skip tombstones and keep
probing. `add` may **reuse** the first tombstone it passed, but only after probing on to an empty
slot to be sure the item is not already stored further along.

**Resizing.** Before adding a **new** item, if `(fill + 1) * 3 > capacity * 2` (the table would
be more than 2/3 full), rebuild the table: the new capacity is the smallest power of two, at
least 8, for which `(used + 1) * 3 <= capacity * 2`. Re-insert only the live items (tombstones
disappear, so `fill == used` afterwards). Removing never shrinks the table.

Write:

- `add(item)`, `discard(item)` (no error if missing), `remove(item)` (`KeyError` if missing),
  `__contains__`, `__len__`, `__iter__` (each live item once, in slot order), and the property
  `capacity` (already there).
- `union(other)`, `intersection(other)`, `difference(other)`: return a **new** `ToySet`; `other`
  may be any iterable. Also the operators `|`, `&`, `-`.
- `__eq__`: equal to another `ToySet` or a built-in `set` with the same items.

`hash()` raises `TypeError` for unhashable items such as lists; let that error through.

**Example**

```python
>>> s = ToySet(["a", "b", "a"])
>>> len(s), "a" in s, "z" in s
(2, True, False)
>>> s.capacity
8
>>> for i in range(10):
...     s.add(i)
>>> len(s), s.capacity               # 12 items would fill more than 2/3 of 16 slots
(12, 32)
>>> s.remove("a"); "b" in s
True
>>> sorted(ToySet([1, 2, 3]) & ToySet([2, 3, 4]))
[2, 3]
```
