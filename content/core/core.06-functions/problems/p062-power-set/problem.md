# All subsets

Write `subsets(items, *, max_size=None)` that returns a list of **all subsets** of the list
`items` (the "power set"), each subset as a list.

- Inside each subset, items keep their order from `items`.
- The subsets themselves may be in **any order**.
- If `max_size` is given, include only subsets with at most `max_size` items.
- It must be recursive, must not import `itertools`, and must not change `items`.

All items are different.

**Examples**

```python
subsets([])               # [[]]
subsets(["a"])            # [[], ['a']]        (any order)
subsets(["a", "b", "c"])
# 8 subsets: [], ['a'], ['b'], ['c'], ['a', 'b'], ['a', 'c'], ['b', 'c'], ['a', 'b', 'c']
subsets([1, 2, 3], max_size=1)
# [], [1], [2], [3]
len(subsets(list(range(12))))   # 4096
```
