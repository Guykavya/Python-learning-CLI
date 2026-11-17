# Sift down

After a pop, the last item is moved to the root; it is probably too big, so it must **sink** (chapter section 3). Write that step as a function that works **in place**:

```python
sift_down(a, i, n)
```

Only the first `n` items of `a` are the heap (`a[:n]`); the items at index `n` and later are **not part of it** and must not move or be looked at. The subtrees below index `i` are valid min-heaps; only `a[i]` may be larger than a child. Move it down:

1. look at the children of `i` that exist (index `< n`);
2. if none of them is smaller than `a[i]`, stop;
3. otherwise swap `a[i]` with the **smaller** child and continue from that child's index.

The children of `i` are `2*i + 1` and `2*i + 2` (0-based). The function changes `a` and returns nothing. When both children are equal, take the left one.

## Example

```python
>>> a = [9, 3, 2, 7, 4, 5, 6]
>>> sift_down(a, 0, 7)
>>> a
[2, 3, 5, 7, 4, 9, 6]

>>> b = [9, 3, 2, 7, 4, 5, 1]    # the last item is NOT in the heap when n = 6
>>> sift_down(b, 0, 6)
>>> b
[2, 3, 5, 7, 4, 9, 1]
```

In the first example `9` swaps with `2` (smaller than `3`), then with `5` (smaller than `6`) and becomes a leaf. In the second `n = 6`, so the item `1` at index 6 does not exist for the heap: `9` still swaps with `2`, then with `5`, and the `1` stays where it is.

## Constraints

- Do not import `heapq`, and do not call `sorted` or `.sort`; the tests check your source.
- `O(log n)` time, `O(1)` extra memory.
- `0 <= i < n <= len(a)`.

## Think about

Why the **smaller** child? Take `[9, 3, 2]`: what happens to the heap property if `9` swaps with `3` instead of `2`? And why does heap sort (section 6) need the argument `n`?
