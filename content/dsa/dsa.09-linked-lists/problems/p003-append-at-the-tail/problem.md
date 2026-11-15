# Append at the tail

Write `append(head, val)`: add a new node holding `val` at the **end** of the chain and return the head of the result.

- If the chain is empty (`head is None`), the new node **is** the whole list, so return it.
- Otherwise walk to the **last** node (the one whose `next` is `None`), link the new node after it, and return the **same** head as before.

The existing nodes must stay the same objects; only the last node's `next` changes.

## Example

```python
>>> head = append(None, 1)          # 1
>>> head = append(head, 2)          # 1 -> 2
>>> head = append(head, 3)          # 1 -> 2 -> 3
>>> to_list(head)
[1, 2, 3]
```

## Constraints

- Up to about 2,000 nodes in the tests; `O(n)` per call is expected (there is no tail pointer here).

## Think about

To change the last node's `next` you must stop **on** the last node, not after it. What loop condition stops there? Why does an `append` without a tail pointer cost `O(n)`, and why is building a list of `n` items with repeated `append` then `O(n^2)`?
