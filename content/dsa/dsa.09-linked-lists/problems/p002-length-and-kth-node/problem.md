# Length and k-th node

A linked list has no `len()` and no `[k]`. You walk.

Write:

1. `length(head)`: the number of nodes in the chain starting at `head` (`0` for `None`).
2. `get(head, k)`: the **node** at index `k` (0-based, like a Python list), or `None` if there is no such node. A negative `k` also gives `None` (no counting from the end here).

`get` returns the node object itself, not its value, so the caller can then change it or link after it.

## Example

```python
>>> head = from_list([10, 20, 30])        # 10 -> 20 -> 30
>>> length(head), length(None)
(3, 0)
>>> get(head, 0) is head
True
>>> get(head, 2).val
30
>>> get(head, 3) is None, get(head, -1) is None
(True, True)
```

`starter.py` contains `ListNode` (and `from_list` is only used in the example; the tests build lists themselves).

## Constraints

- Up to `10**5` nodes; use loops.
- Neither function may change the chain.

## Think about

How many `next` steps does it take to reach index `k`? What happens if you take one step too many on a list of length `k`?
