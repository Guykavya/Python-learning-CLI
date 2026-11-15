# Reverse in groups of k

Write `reverse_k_group(head, k)` that reverses the nodes of the list **k at a time** and returns the new head. If the number of nodes left at the end is smaller than `k`, those last nodes stay in their original order. Rewire nodes; do not create nodes or change values.

## Example

```python
>>> to_list(reverse_k_group(from_list([1, 2, 3, 4, 5]), 2))
[2, 1, 4, 3, 5]
>>> to_list(reverse_k_group(from_list([1, 2, 3, 4, 5]), 3))
[3, 2, 1, 4, 5]
>>> to_list(reverse_k_group(from_list([1, 2, 3]), 1))        # groups of one: unchanged
[1, 2, 3]
```

## Constraints

- `1 <= k`; the list has `0` to `10**5` nodes (`k` may be larger than the list).
- `O(n)` time and `O(1)` extra memory (no Python list of nodes, no recursion over groups).

## Think about

Before you reverse a group you must know that it is **complete**: how do you check that without losing your place? After a group is reversed, which node is the "node before the next group"?
