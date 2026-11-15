# Copy a list with random pointers

Each node (`RNode`, given in `starter.py`) has `val`, `next`, and a third pointer `random` that points to **any** node of the same list, or to `None` (chapter section 10).

Write `copy_random_list(head)` that returns a **deep copy**: a new list of new nodes with the same values, where

- the copy's `next` pointers give the same order;
- each copy's `random` points to the **copy** of the node that the original's `random` points to (never into the original list);
- **no node is shared** between the original and the copy;
- the **original list is unchanged** at the end (its `next` and `random` pointers).

## Example

```text
original:  7 -> 13 -> 11 -> 10 -> 1 -> None
random:    7: None, 13: 7, 11: 1, 10: 11, 1: 7
```

As `[value, index of the random target]` pairs: `[[7, None], [13, 0], [11, 4], [10, 2], [1, 0]]`. The copy has exactly the same pairs, but every node in it is new.

## Constraints

- `0 <= n <= 10**4`. Values may repeat, so you cannot find a node by its value.

Two good methods: a dictionary `original -> copy` (two passes, `O(n)` extra memory), or the **interleaving** method that needs no dictionary: put each copy right after its original, set the randoms, then separate the two lists (and restore the original!).

## Think about

When you create the copy of node `A`, the node `A.random` may not have a copy yet. How do the two methods get around that?
