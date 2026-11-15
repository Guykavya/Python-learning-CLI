# Intersection of two lists

Two singly linked lists may **share** their tail: from some node on, both lists continue through the very same node objects.

```text
a:       4 -> 1 \
                 8 -> 4 -> 5 -> None
b:  5 -> 6 -> 1 /
```

Write `get_intersection(a, b)` that returns the **first shared node** (here the node holding `8`), or `None` if the lists share no node.

- "Shared" means the same object (`is`), not an equal value: in the picture both lists contain a `1`, but those are two different nodes.
- `O(1)` extra memory (no set of nodes; the tests measure it), and do not change either list.

## Example

With the lists above, `get_intersection(a, b)` returns the node holding `8` (that node object itself). For `a = 1 -> 2` and `b = 1 -> 2` built separately, it returns `None`.

## Constraints

- Each list has `0` to `10**5` nodes; the lists can have different lengths. Neither list has a cycle.

## Think about

If both lists had the **same** length before the shared part, how would you find the shared node? Now: pointer `p` walks `a` and then `b`; pointer `q` walks `b` and then `a`. How many steps does each take to reach the shared node?
