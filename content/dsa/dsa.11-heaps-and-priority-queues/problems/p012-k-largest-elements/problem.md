# K largest elements

Write `k_largest(nums, k)`. It returns a **list** with the `k` largest items of `nums`, **largest first**. This is the top-K algorithm of chapter section 7: keep a **min**-heap of size `k`.

For each item `x`:

- if the heap holds fewer than `k` items, push `x`;
- otherwise, if `x` is larger than the root `heap[0]` (the weakest of the `k` kept items), replace the root with `x`;
- otherwise ignore `x`.

At the end the heap holds the `k` largest items. Take them out in the right order.

Rules:

- If `k <= 0` the answer is `[]`. If `k` is at least the number of items, the answer is all the items, largest first.
- Equal items are all kept (`[4, 4, 4]` with `k = 2` gives `[4, 4]`).
- `nums` can be any iterable (a list, a tuple, a generator); it is read **once** and never changed.
- Do not call `sorted`, `.sort`, `heapq.nlargest` or `heapq.nsmallest`; the tests check your source. Getting the descending order out of the heap is part of the exercise: the pops come out smallest first, so reverse them.
- The tests **count comparisons** (a wrapper class that counts every `<`, `>`, ...): on `20,000` items the answer must need at most `4 * 20,000` comparisons. Looking at the weakest kept item first (`x > heap[0]`) is what makes most items cost only one comparison.

## Example

```python
>>> k_largest([3, 1, 5, 12, 2, 11, 7], 3)
[12, 11, 7]
>>> k_largest([4, 4, 4], 2)
[4, 4]
>>> k_largest([1, 2], 5)
[2, 1]
>>> k_largest([1, 2], 0)
[]
```

## Constraints

- `O(n log k)` time, `O(k)` extra memory. `0 <= len(nums) <= 10**5`, `-10**9 <= x <= 10**9`.

## Think about

Why a **min**-heap to keep the **largest** items? What happens to the size of the heap when `k` is bigger than `n`, and why must you handle `k = 0` before you look at `heap[0]`?
