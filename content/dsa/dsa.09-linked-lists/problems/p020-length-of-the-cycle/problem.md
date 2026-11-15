# Length of the cycle

Write `cycle_length(head)` that returns the number of nodes in the cycle of the chain, or `0` if there is no cycle.

Find a node inside the cycle with fast and slow pointers (the meeting point of problem 17). From there, walk once round the cycle and count the steps until you are back on the same node.

Rules: `O(1)` extra memory (the test nodes cannot be hashed or marked), and do not change the list.

## Example

```text
0 -> 1 -> 2 -> 3 -> 4 -> 5 -> 6
               ^              |
               +--------------+        cycle_length is 4  (3, 4, 5, 6)

5 -> 5 (pointing to itself)            cycle_length is 1
1 -> 2 -> None                         cycle_length is 0
```

## Constraints

- Up to `10**5` nodes.

## Think about

Why can you not count from the head? Why is any node of the cycle a good starting point for counting, not only the first one?
