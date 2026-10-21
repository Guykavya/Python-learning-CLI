# Binary search by recursion

Write `binary_search(items, target, lo=0, hi=None)` that searches the **sorted** list `items`
for `target` and returns its index, or `-1` if it is absent. If `target` occurs several times,
any matching index is fine.

Rules:

- It must be **recursive**: each call looks at the middle of `items[lo:hi]` and recurses on one
  half.
- Do **not** slice the list (`items[...:...]`); slicing copies, making every call O(n). Pass the
  indices `lo` and `hi` instead. `hi=None` means "the end of the list".
- The caller calls it with just `(items, target)`.

**Examples**

```python
data = [2, 5, 8, 12, 16, 23, 38, 56, 72, 91]
binary_search(data, 23)    # 5
binary_search(data, 2)     # 0
binary_search(data, 91)    # 9
binary_search(data, 7)     # -1
binary_search([], 1)       # -1
```
