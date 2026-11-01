# Model a compact dict

Since Python 3.6 a CPython `dict` is stored in two parts (the "compact dict"):

- **`entries`**: a list of `[hash, key, value]` in insertion order. Iterating the dict walks this
  list, which is why dicts keep insertion order.
- **`indices`**: the hash table itself, a small array whose length is a power of two. Each slot
  is empty, or holds the *position* of an entry in `entries`, or is a **tombstone** meaning "an
  entry used to be here".

To find a key, start at slot `hash(key) & (capacity - 1)` and step forward until you find the key
or reach an empty slot. Real CPython uses a cleverer step pattern ("perturbation"); you will use
**linear probing**: the next slot is `(slot + 1) & (capacity - 1)`, wrapping around at the end.

Copy `starter.py` to `solution.py` and finish `ToyDict`. Keep these attribute names, because
the tests look inside:

- `self.indices`: a list of length `capacity` (starts at 8). Each slot is `None` (free), the
  module constant `DELETED` (tombstone) or an `int` index into `entries`.
- `self.entries`: a list whose items are `[hash, key, value]` lists, or `None` for a deleted entry.
- `capacity`: a property, `len(self.indices)`.

Rules:

1. **Lookup** of `key` with `h = hash(key)`: probe from `h & (capacity - 1)`. A free slot (`None`)
   ends the search: the key is absent. A tombstone does **not** end it: skip it and keep going.
   An index slot matches when the stored key `is key`, or when the stored hash equals `h` and the
   stored key `== key` (the same test CPython uses).
2. **Setting an existing key** replaces its value in place (its position in the order stays).
3. **Adding a new key**: first, if `len(self.entries) + 1 > capacity * 2 // 3`, **resize**. Then
   append `[h, key, value]` to `entries` and store its index in the **first free or tombstone slot**
   on the key's probe path.
4. **Deleting**: put `DELETED` in the key's slot and `None` in its place in `entries`.
   Missing key: `KeyError`.
5. **Resize**: keep only the live entries (in order), choose the smallest capacity, a power of two
   that is at least 8, with `len(live) + 1 <= capacity * 2 // 3`, and rebuild `indices` from
   scratch (no tombstones afterwards).

Also provide `__getitem__` (`KeyError` when missing), `__contains__`, `__len__` (live keys),
`__iter__` (keys in insertion order), `get(key, default=None)` and `items()` (a list of
`(key, value)` pairs in order).

**Example**

```python
d = ToyDict()
d[1] = "a"           # hash(1) == 1, slot 1 & 7 = 1
d[9] = "b"           # hash(9) == 9, 9 & 7 = 1 is taken -> slot 2
d.indices            # [None, 0, 1, None, None, None, None, None]
del d[1]
d.indices            # [None, DELETED, 1, None, None, None, None, None]
d.entries            # [None, [9, 9, 'b']]
d[9]                 # 'b'   (the search skips the tombstone in slot 1)
d[17] = "c"          # 17 & 7 = 1: a tombstone, reused for the new key
d.indices[1]         # 2
list(d), len(d)      # ([9, 17], 2)
```

`hash()` of a small `int` is the int itself on every Python version, which makes the slots easy
to predict. `hash()` of a `str` changes every time Python starts (hash randomisation), so never
predict string slots.
