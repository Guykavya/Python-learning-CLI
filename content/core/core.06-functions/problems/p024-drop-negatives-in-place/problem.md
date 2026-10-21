# Remove negatives in place

Write `drop_negatives(numbers)` that removes every negative number from the caller's list,
**in place**, keeping the order of the rest, and returns `None`.

The caller's list object must be the one that changes; other names referring to it see the
change too.

**Example**

```python
data = [3, -1, 4, -5, 0, -9]
alias = data
drop_negatives(data)
data     # [3, 4, 0]
alias    # [3, 4, 0]     (same list)
```

Be careful: removing items from a list **while looping over it** skips items (core.05).
