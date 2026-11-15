# Remove the n-th node from the end

Write `remove_nth_from_end(head, n)` that removes the `n`-th node **counted from the end** (`n = 1` is the last node) and returns the head of the result.

Do it in **one pass**, without first counting the length: move a `fast` pointer `n` nodes ahead, then move `fast` and `slow` together. The fixed gap leaves `slow` just before the node to remove when `fast` reaches the last node. A dummy node in front handles removing the head (`n` equal to the length).

## Example

```python
>>> to_list(remove_nth_from_end(from_list([1, 2, 3, 4, 5]), 2))
[1, 2, 3, 5]
>>> to_list(remove_nth_from_end(from_list([1, 2, 3]), 3))      # n = length removes the head
[2, 3]
>>> remove_nth_from_end(from_list([7]), 1) is None
True
```

## Constraints

- The list has `1` to `10**5` nodes, and `1 <= n <= length`. `O(1)` extra memory.

## Think about

How big must the gap between `fast` and `slow` be so that `slow` stops on the node **before** the one to remove? Check with `n = 1` on a list of 3.
