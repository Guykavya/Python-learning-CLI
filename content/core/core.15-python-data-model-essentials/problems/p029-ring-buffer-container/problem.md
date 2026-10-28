# A ring buffer that behaves like a container

A ring buffer keeps only the **last N** items: when it is full, a new item overwrites the oldest
one. Logs, "last 5 commands" and audio streams use it. Write `RingBuffer` in `solution.py`.

- `RingBuffer(capacity)`: `capacity` below 1 raises `ValueError`. The attribute `capacity` stores it.
- `append(item)`: adds the item. If the buffer is full, the **oldest** item is dropped.
- `is_full()`: `True` when it holds `capacity` items.
- `len(rb)`: how many items are stored now (never more than `capacity`).
- `rb[i]`: the i-th item counted from the **oldest** (`rb[0]`) to the newest (`rb[len(rb) - 1]`).
  Negative indices count from the newest: `rb[-1]` is the newest. A bad index raises `IndexError`;
  a non-integer index (such as a slice or a string) raises `TypeError`.
- `iter(rb)` / `for x in rb`: items from oldest to newest. Every `iter(rb)` starts again from the
  beginning, so two loops over the same buffer both see all items.
- `repr(rb)`: `RingBuffer([1, 2], capacity=3)` (the items oldest first, written with `repr`).

Do not use `collections.deque`: the goal is to practise the protocol methods. Once `__len__` and
`__iter__` exist, `in`, `sum`, `max`, `sorted`, `list` and truthiness work without more code.

**Example**

```python
rb = RingBuffer(3)
for n in (1, 2, 3, 4, 5):
    rb.append(n)
list(rb)       # [3, 4, 5]
rb[0], rb[-1]  # (3, 5)
len(rb)        # 3
4 in rb        # True
rb             # RingBuffer([3, 4, 5], capacity=3)
```
