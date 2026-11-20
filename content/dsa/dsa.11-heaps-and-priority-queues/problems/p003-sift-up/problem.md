# Sift up

When a new item is pushed into a heap, it is appended at the end of the list, and then it **bubbles up** while it is smaller than its parent (chapter section 3). Write that step as a function that works **in place**:

```python
sift_up(a, i)
```

The list `a` is a valid min-heap **except possibly at index `i`**: the item `a[i]` may be smaller than its parent. Move it up: while `i > 0` and `a[i]` is **strictly smaller** than its parent, swap them and continue from the parent's index. Stop when the parent is not larger, or at the root.

The function changes `a` and returns nothing. Layout: 0-based, the parent of index `i` is `(i - 1) // 2`.

## Example

```python
>>> a = [2, 5, 3, 9, 6]      # a valid min-heap
>>> a.append(1)              # now 1 is a child of 3 (index 5, parent index 2)
>>> sift_up(a, 5)
>>> a
[1, 5, 2, 9, 6, 3]
```

Step by step: `1 < 3`, swap with the parent at index 2: `[2, 5, 1, 9, 6, 3]`; then `1 < 2`, swap with the parent at index 0: `[1, 5, 2, 9, 6, 3]`; index 0 is the root, stop.

The same function repairs a heap after an item has been **made smaller**: set `a[i] = something_smaller`, then call `sift_up(a, i)`.

## Constraints

- Do not import `heapq`, and do not call `sorted` or `.sort`. The whole point is to write the step yourself; the tests check your source.
- `O(log n)` time, `O(1)` extra memory.
- `0 <= i < len(a)`.

## Think about

How many swaps can one call do at most, for a heap of 1,000,000 items? And why does only the path from `i` to the root change, never the other items?
