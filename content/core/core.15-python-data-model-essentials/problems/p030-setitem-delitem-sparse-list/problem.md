# A sparse list with item assignment and deletion

A spreadsheet row with a million cells where only three have a value should not take a million
slots. A **sparse list** stores only the positions that differ from a default value. Write
`SparseList` in `solution.py`.

- `SparseList(size, default=0)`: a list-like object of `size` positions that all start as `default`.
  A negative `size` raises `ValueError`. Keep the values in a **dict** from position to value; do
  not build a real list of `size` items.
- `len(s)`: the logical size.
- `s[i]`: the value at position `i`, or `default` if nothing is stored there. Negative indices work
  like a list's. A position out of range raises `IndexError`; a non-integer index raises `TypeError`.
- `s[i] = value`: sets a position (same index rules). If `value == default` the entry is **removed**
  from the dict instead of stored.
- `del s[i]`: removes the position like `del` on a list: everything after it moves one place left
  and `len(s)` goes down by one.
- `iter(s)`: yields all `len(s)` values in order, defaults included.
- `s.stored_count` (a property): how many positions are stored in the dict.
- `repr(s)`: `SparseList([0, 4, 0], default=0)`.

Slices are not required.

**Example**

```python
s = SparseList(5)
s[1] = 7
s[-1] = 9
list(s)           # [0, 7, 0, 0, 9]
s.stored_count    # 2
del s[0]
list(s)           # [7, 0, 0, 9]
len(s)            # 4
```
