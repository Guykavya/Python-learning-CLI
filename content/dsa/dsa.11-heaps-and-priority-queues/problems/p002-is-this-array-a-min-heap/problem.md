# Is this array a min-heap?

A list `a` is a **min-heap** when every item is less than or equal to its children (chapter section 2). With the 0-based layout, the children of index `i` are at `2*i + 1` and `2*i + 2`. Items that would lie outside the list do not exist.

Write `is_min_heap(a)`. It returns `True` when the list satisfies the heap property and `False` otherwise. It must **not change** the list.

## Example

```python
>>> is_min_heap([1, 3, 2, 7, 4, 5, 6])
True
>>> is_min_heap([1, 3, 2, 7, 4, 5, 0])     # 0 is a child of 2: smaller than its parent
False
>>> is_min_heap([2, 2, 2])                 # equal items are fine
True
>>> is_min_heap([])
True
>>> is_min_heap([5])
True
```

Notice: a sorted list (smallest first) is always a heap, but a heap is **not** always sorted. `[1, 3, 2]` is a heap, and it is not sorted.

## Constraints

- `0 <= len(a) <= 10**5`. One pass: `O(n)` time, no extra list.
- Items can be compared with `<`/`>` (numbers or strings; do not assume ints).

## Think about

You do not need to look at every pair of neighbours. Which items must you compare with which? It is enough to check every **non-leaf** item against its children. Which indexes are the non-leaf ones?
