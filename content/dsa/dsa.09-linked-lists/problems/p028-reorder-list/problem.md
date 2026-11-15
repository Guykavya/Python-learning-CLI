# Reorder list

Rearrange the list `L0 -> L1 -> ... -> Ln-1 -> Ln` **in place** into

```text
L0 -> Ln -> L1 -> Ln-1 -> L2 -> Ln-2 -> ...
```

(first, last, second, second-last, ...). Write `reorder_list(head)`; it changes the links of the given nodes and returns `None` (like `list.sort()`): the caller keeps using `head`, which stays the first node.

Do not create nodes, do not change values, and do not copy the nodes into a Python list: `O(1)` extra memory. Plan (chapter section 9): find the middle, cut, reverse the second half, then weave the two halves together.

## Example

```python
>>> head = from_list([1, 2, 3, 4, 5])
>>> reorder_list(head)
>>> to_list(head)
[1, 5, 2, 4, 3]
>>> head = from_list([1, 2, 3, 4]); reorder_list(head); to_list(head)
[1, 4, 2, 3]
```

## Constraints

- `0 <= n <= 10**5`.

## Think about

After cutting and reversing, `[1, 2, 3, 4, 5]` becomes `1 -> 2 -> 3` and `5 -> 4`. In the weave, which two `next` pointers change per round, and which two nodes must you save first?
