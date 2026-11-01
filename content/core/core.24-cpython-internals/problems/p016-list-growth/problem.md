# Watch a list grow

A CPython `list` is a **dynamic array**: a block of slots (one pointer per item) plus a count of
how many slots are used. When `append` finds the block full, CPython allocates a bigger block,
copies the pointers over and frees the old block. If it grew by one slot each time, `n` appends
would copy `1 + 2 + ... + n` pointers: O(n²). Instead it **over-allocates**: it asks for extra
room (about 1/8 more, plus a few slots), so most appends just fill a spare slot. Copies happen
rarely and the average cost of an append is O(1) ("amortised" O(1)).

`sys.getsizeof(lst)` includes the slot block, so its value only changes when the list
reallocates. You can watch the growth from Python.

Copy `starter.py` to `solution.py` and write three functions.

**`growth_points(n)`** starts with an empty list, appends `n` items one at a time (any value,
for example `None`) and returns the list of lengths **right after the append that changed
`sys.getsizeof`**. Compare each new size with the previous size (start with the size of the empty
list).

**`copy_cost(n)`** uses a simple model: at each growth point `p`, the `p - 1` items already in
the list are copied into the new block. Return the total number of copied items for `n` appends.

**`capacity(lst)`** returns how many item slots `lst` currently has, used or not:
`(sys.getsizeof(lst) - sys.getsizeof([])) // struct.calcsize("P")`. (`struct.calcsize("P")`
is the size of one pointer, 8 bytes on a 64-bit Python.)

**Version warning.** The exact growth points, and all `getsizeof` numbers, are implementation
details: they differ between Python versions and between 32-bit and 64-bit builds. The tests
check only relations that any over-allocating list must satisfy, never the numbers below.

**Example**

```python
growth_points(20)      # Python 3.14, 64-bit (yours may differ): [1, 5, 9, 17]
copy_cost(20)          # 0 + 4 + 8 + 16 = 28 with the points above
lst = []
for i in range(5):
    lst.append(i)
len(lst), capacity(lst)  # (5, 8) on Python 3.14, 64-bit: three spare slots
capacity([])           # 0 on every version: an empty list owns no slot block
```
