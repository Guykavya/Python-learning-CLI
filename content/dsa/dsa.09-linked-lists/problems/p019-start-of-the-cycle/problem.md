# Start of the cycle

Write `detect_cycle(head)` that returns the **first node of the cycle** (the node where the walk from the head enters the loop), or `None` if the chain has no cycle.

Use Floyd's two phases (chapter section 7, "Where does the cycle start?"):

1. `slow` and `fast` move as in problem 17 until they meet.
2. Put a pointer `p` back on the head. Move `p` and `slow` **one step each** until they are the same node. That node is the start of the cycle.

Rules: `O(1)` extra memory (no set, dict or list of nodes; the test nodes cannot be hashed or marked), and do not change the list.

## Example

A tail of 3 nodes and a cycle of 4 nodes:

```text
0 -> 1 -> 2 -> 3 -> 4 -> 5 -> 6
               ^              |
               +--------------+        6.next is 3
```

`detect_cycle(head)` returns the node holding `3` (the node object itself). For `0 -> 1 -> 2 -> None` it returns `None`.

## Constraints

- Up to `10**5` nodes. The tail before the cycle can be empty (the head is in the cycle), and the cycle can have length 1.

## Think about

Trace the example on paper: where do `slow` and `fast` meet? Then count: from the meeting point, how many steps forward is node `3`? How many steps is node `3` from the head? Why are those two numbers related?
