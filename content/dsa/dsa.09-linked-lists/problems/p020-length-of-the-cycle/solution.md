## Approach

Find the meeting point of `slow` and `fast`. It is inside the cycle, and every node of a cycle leads round the whole cycle back to itself. So walk from it and count the steps until you return. No meeting means no cycle: return `0`.

## Code

```python
def cycle_length(head):
    slow = fast = head
    while fast is not None and fast.next is not None:
        slow = slow.next
        fast = fast.next.next
        if slow is fast:                 # inside the cycle: walk once round it
            length = 1
            cur = slow.next
            while cur is not slow:
                cur = cur.next
                length += 1
            return length
    return 0
```

## Complexity

`O(n)` time: phase 1 is `O(n)`, the extra lap is `L <= n` steps. `O(1)` extra memory.

## Another way

Keep walking `slow` and `fast` after the first meeting and count the rounds until they meet again: `fast` gains one node per round, so the next meeting is exactly one lap (`L` rounds) later. Or, with problem 19's answer, walk from the cycle start until you are back at it.
