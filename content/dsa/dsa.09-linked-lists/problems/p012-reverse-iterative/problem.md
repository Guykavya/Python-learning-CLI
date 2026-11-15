# Reverse a list (iterative)

Write `reverse_list(head)` that reverses the chain **in place** and returns the new head.

"In place" means: do not create any new nodes and do not change any `val`. Turn the `next` arrows around, so that the same node objects are linked in the opposite order. Use a loop with three variables (`prev`, `cur`, `nxt`, chapter section 6).

## Example

```python
>>> to_list(reverse_list(from_list([1, 2, 3, 4])))
[4, 3, 2, 1]
>>> reverse_list(None) is None
True
```

## Constraints

- Up to `10**5` nodes, so a loop, not recursion. `O(n)` time, `O(1)` extra memory.

## Think about

Which node becomes the new head, and which node must end up with `next = None`? What would be lost if you flipped an arrow before saving where it pointed?
