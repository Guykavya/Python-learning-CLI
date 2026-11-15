# Merge two sorted lists

`a` and `b` are the heads of two lists, each sorted in non-decreasing order. Write `merge_two(a, b)` that links their nodes into **one** sorted list and returns its head.

- Reuse the nodes: create no node except one dummy, and do not change any `val`.
- **Stable**: when a node of `a` and a node of `b` have equal values, the node of `a` comes first.

## Example

```python
>>> to_list(merge_two(from_list([1, 2, 4]), from_list([1, 3, 4])))
[1, 1, 2, 3, 4, 4]          # each first 1 and first 4 come from a
>>> to_list(merge_two(None, from_list([0])))
[0]
```

## Constraints

- Each list has `0` to `10**5` nodes. `O(n + m)` time, `O(1)` extra memory, no recursion.

## Think about

When one list runs out, how many nodes of the other list must you still link one by one?
