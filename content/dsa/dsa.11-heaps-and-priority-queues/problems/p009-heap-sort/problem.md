# Heap sort

Write the in-place heap sort of chapter section 6:

```python
heap_sort(a, reverse=False)
```

It sorts the list `a` **in place**: after the call, `a` itself is sorted, smallest first (largest first when `reverse=True`). The return value is not checked (the chapter version returns `a`; returning `None` is fine too).

The method has two phases:

1. **Build** a heap inside the list, bottom-up: `sift_down` from the last parent back to the root. For an ascending sort the heap is a **max**-heap (the root is the largest item); for `reverse=True` it is a **min**-heap.
2. **Move the root to the back**: swap the root with the last item of the heap part, shrink the heap by one, `sift_down` the new root. Repeat until the heap has one item. The sorted part grows from the right.

## Example

```python
>>> a = [4, 10, 3, 5, 1]
>>> heap_sort(a)
>>> a
[1, 3, 4, 5, 10]

>>> heap_sort(a, reverse=True)
>>> a
[10, 5, 4, 3, 1]
```

After phase 1 the list `[4, 10, 3, 5, 1]` is the max-heap `[10, 5, 3, 4, 1]`; the first swap of phase 2 gives `[1, 5, 3, 4 | 10]`, and after the sift-down `[5, 4, 3, 1 | 10]`.

## Constraints

- Do not import `heapq` and do not call `sorted` or `.sort`; the tests check your source.
- In place, `O(1)` extra memory: do not copy the list and do not build a second one.
- `O(n log n)` time. The tests count comparisons on 2,000 items: a selection sort or a bubble sort will fail.
- Items can be anything comparable (numbers, strings). Duplicates are allowed; heap sort is **not stable**, so the tests never depend on the order of equal items.
- `0 <= len(a) <= 10**5`.

## Think about

Why a **max**-heap for an ascending sort? Where does the largest item go in the first step of phase 2, and why is that its final place? And why must `sift_down` in phase 2 be told where the heap ends?
