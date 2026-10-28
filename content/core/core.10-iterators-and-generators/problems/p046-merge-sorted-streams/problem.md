# Merge sorted streams lazily

Three servers each send their log records **already sorted by time**. You want one stream, also
sorted by time, without collecting everything first (the streams may be endless).

Write a generator function `merge_sorted(*iterables, key=None)` in `solution.py`.

- Each input is sorted (by `key(item)`, or by the item itself if `key` is `None`).
- Yield all items of all inputs, in sorted order.
- **Ties:** if two items have equal keys, the one from the **earlier** input comes first.
- **Lazy:** hold at most **one** waiting item per input. Never call `list()`, `sorted()` or
  `sort()` on the inputs. Inputs may be infinite.
- Do not use `heapq` (you will meet it later). Find the smallest of the waiting items yourself.

**Examples**

```python
list(merge_sorted([1, 4, 7], [2, 3, 9], [5]))      # [1, 2, 3, 4, 5, 7, 9]
list(merge_sorted([], [1, 1], [1]))                # [1, 1, 1]
list(merge_sorted())                               # []

a = [{"t": 1, "src": "a"}, {"t": 5, "src": "a"}]
b = [{"t": 1, "src": "b"}, {"t": 2, "src": "b"}]
[r["src"] for r in merge_sorted(a, b, key=lambda r: r["t"])]
# ["a", "b", "b", "a"]      (t=1 from a comes before t=1 from b: a is the earlier input)
```
