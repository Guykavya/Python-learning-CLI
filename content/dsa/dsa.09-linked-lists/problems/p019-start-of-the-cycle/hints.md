## Hint 1

Phase 1 is exactly problem 17, except that on the meeting you do not return `True`: you keep the meeting node in `slow`. If the loop ends without a meeting, there is no cycle.

## Hint 2

Phase 2: `p = head`. While `p is not slow`, move both one step. Why does the loop end on the cycle start? Let the tail have `a` nodes; when they met, `slow` had walked `a + b` steps and `fast` twice that. The extra `a + b` steps of `fast` are whole laps of the cycle. So from the meeting point, walking `a` more steps ends on ... ?

## Hint 3

```
slow = fast = head
while fast and fast.next:
    slow = slow.next; fast = fast.next.next
    if slow is fast:
        p = head
        while p is not slow: p = p.next; slow = slow.next
        return p
return None
```
