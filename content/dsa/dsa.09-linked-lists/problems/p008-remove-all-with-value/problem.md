# Remove all nodes with a value

Write `remove_all(head, target)` that removes **every** node whose value equals `target` and returns the head of what is left (`None` if nothing is left).

Use a **dummy node** in front of the head (chapter section 4), so removing the first node is not a special case. Do not create new nodes for the values you keep: the remaining nodes must be the original node objects, in the original order.

## Example

```python
>>> to_list(remove_all(from_list([6, 6, 1, 6, 2, 6]), 6))
[1, 2]
>>> remove_all(from_list([7, 7]), 7) is None
True
>>> to_list(remove_all(from_list([1, 2, 3]), 9))
[1, 2, 3]
```

## Constraints

- Up to `10**5` nodes; one pass, `O(1)` extra memory.

## Think about

After you unlink `prev.next`, the node that slid into its place has not been checked yet. Should `prev` move forward in that case?
