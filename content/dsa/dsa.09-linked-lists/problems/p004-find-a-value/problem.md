# Find a value

Write `find(head, target)` that returns the **index** (0-based) of the first node whose value equals `target`, or `-1` if no node holds it. The chain must not change.

## Example

```python
>>> head = from_list([4, 7, 1, 7])
>>> find(head, 7)            # the first 7 is at index 1
1
>>> find(head, 4), find(head, 9), find(None, 4)
(0, -1, -1)
```

## Constraints

- Up to `10**5` nodes; values can be any objects that support `==` (numbers, strings, `None`).

## Think about

You need two things at once while walking: the node and its index. Which two variables do you keep, and do they always move together?
