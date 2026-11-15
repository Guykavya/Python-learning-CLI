# Detect a cycle

A chain has a **cycle** when some node's `next` points back to a node earlier in the chain: a walk from the head then never reaches `None`. Write `has_cycle(head)` that returns `True` if the chain has a cycle and `False` otherwise.

Use **Floyd's tortoise and hare** (chapter section 7): `slow` moves one step, `fast` two steps. If there is no cycle, `fast` reaches the end. If there is one, `fast` laps `slow` inside the cycle and they land on the **same node**.

Rules:

- `O(1)` extra memory: no set or dict of nodes (or of their `id`s), no list of nodes.
- Do not change the list, and do not mark nodes. The tests use nodes that **cannot** be put in a set and **cannot** take extra attributes (they use `__slots__`, see chapter section 14), and they measure the memory your function uses.

## Example

```text
1 -> 2 -> 3 -> 4
          ^    |
          +----+         4.next is 3: has_cycle is True

1 -> 2 -> 3 -> None      has_cycle is False
```

## Constraints

- Up to `10**5` nodes; the cycle may start anywhere, may be the whole list, or may be one node pointing to itself.

## Think about

Why must the test be `slow is fast` and not `slow.val == fast.val`? Once both are inside the cycle, by how much does the distance between them change per round?
