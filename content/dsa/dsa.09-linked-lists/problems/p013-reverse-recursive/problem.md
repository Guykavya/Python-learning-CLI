# Reverse a list (recursive)

Write `reverse_rec(head)` that reverses the chain in place and returns the new head, **using recursion and no loop** (chapter section 6, "Recursive reversal").

Think of it as in dsa.07: "reverse the rest of the list, then attach the first node at the end of the reversed rest." Do not create nodes and do not change values.

## Example

```python
>>> to_list(reverse_rec(from_list([1, 2, 3, 4])))
[4, 3, 2, 1]
>>> reverse_rec(None) is None
True
```

## Constraints

- Up to 800 nodes in the tests. Each call adds one frame to Python's call stack, and Python stops at about 1,000 frames (`RecursionError`). The tests themselves already run a few dozen frames deep, so 800 is a safe size; 2,000 would not be.
- No `for` or `while` loop in your solution (the tests check this).

## Example of the key step

After `reverse_rec(head.next)` returns for `1 -> 2 -> 3`, the rest is `3 -> 2 -> None`, and node `1` still points at node `2` (its `next` was not touched). So `head.next` is the **last** node of the reversed rest. One line makes it point back at `head`; another line cuts `head`'s old arrow.

## Think about

What are the base cases? Which node does every level of the recursion return, and does it ever change on the way back up? Why is the iterative version (problem 12) the right choice for long lists in Python?
