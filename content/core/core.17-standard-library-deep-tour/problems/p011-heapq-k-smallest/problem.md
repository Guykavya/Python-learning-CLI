# heapq: the k smallest and k largest

Sorting a million items to get the top 3 does a lot of wasted work. The `heapq` module keeps
a **min-heap** in a plain list: the smallest item is always at index 0, and pushing or popping
costs O(log n). It also has `nsmallest(k, iterable, key=...)` and `nlargest(k, iterable, key=...)`.

Write three functions in `solution.py`.

1. `k_smallest(nums: Iterable[int], k: int) -> list[int]`: the `k` smallest numbers, ascending.
   Use `heapq.nsmallest`.
2. `top_k_by(records: list[dict], k: int, field: str) -> list[dict]`: the `k` records with the
   **largest** value in `field`, largest first. Records with equal values keep their input order.
3. `pop_k_smallest(nums: list[int], k: int) -> list[int]`: the same answer as `k_smallest`, but
   build it yourself: copy the list, `heapify` the copy, and `heappop` `k` times.
   **Do not change the caller's list.**

In all three, `k <= 0` gives `[]`, and `k` bigger than the input gives everything (sorted).

**Example**

```python
k_smallest([5, 1, 4, 1, 9], 3)            # [1, 1, 4]
top_k_by([{"n": "a", "s": 3}, {"n": "b", "s": 9}, {"n": "c", "s": 3}], 2, "s")
# [{'n': 'b', 's': 9}, {'n': 'a', 's': 3}]   ('a' came before 'c')
nums = [3, 2, 1]
pop_k_smallest(nums, 2)                   # [1, 2]
nums                                      # [3, 2, 1]  unchanged
```
