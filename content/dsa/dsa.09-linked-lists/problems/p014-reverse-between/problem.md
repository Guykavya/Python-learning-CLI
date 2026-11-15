# Reverse between positions

Write `reverse_between(head, left, right)` that reverses only the nodes at positions `left` to `right` (**1-based**, both included) and returns the head of the whole list. Everything outside that range stays in place. Rewire nodes; do not create nodes or change values.

## Example

```python
>>> to_list(reverse_between(from_list([1, 2, 3, 4, 5]), 2, 4))
[1, 4, 3, 2, 5]
>>> to_list(reverse_between(from_list([1, 2, 3]), 1, 3))     # the whole list
[3, 2, 1]
>>> to_list(reverse_between(from_list([1, 2, 3]), 2, 2))     # one node: nothing changes
[1, 2, 3]
```

## Constraints

- `1 <= left <= right <= n`, where `n` (at least 1) is the number of nodes, up to `10**5`.
- One pass, `O(1)` extra memory.

## Think about

Name the four nodes that matter: the node **before** the range, the **first** and **last** nodes of the range, and the node **after** it. After reversing the range, which of them point where? Why does `left = 1` need no special case if you use a dummy?
