## Hint 1

Phase 1 of Floyd gives you a node that is surely **inside** the cycle. Starting from a node inside a cycle, what happens if you keep following `next`?

## Hint 2

Hold the meeting node in `slow`. Walk a second pointer from `slow.next`, counting, until it is `slow` again. Start the count at 1 so that a node pointing to itself gives 1.

## Hint 3

```
phase 1 as in problem 17; on meeting:
    length = 1; cur = slow.next
    while cur is not slow: cur = cur.next; length += 1
    return length
return 0
```
