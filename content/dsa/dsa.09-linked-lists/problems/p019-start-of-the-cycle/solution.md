## Approach

Phase 1 finds **a** node inside the cycle (the meeting point). Phase 2 finds the **first** node of the cycle: one pointer from the head, one from the meeting point, both one step at a time; they meet exactly at the start.

## Why it works

Let the tail before the cycle have `a` nodes, the cycle have length `L`, and let the meeting point be `b` steps into the cycle. At the meeting, `slow` walked `a + b` steps and `fast` walked `2(a + b)`. Both are on the same node, so the difference `a + b` is a whole number of laps: `a + b = kL`. Hence `a = kL - b`: walking `a` steps from the meeting point is the same as walking `L - b` steps (to the start of the cycle) and then some whole laps. Meanwhile `p` walks `a` steps from the head and also reaches the start. They meet there, and not earlier, because before that `p` is still in the tail and `slow` is in the cycle.

## Hand trace: tail 3, cycle 4

Output of a version with prints (the list of the example, `6.next` is `3`):

```text
phase 1, round 1: slow=1 fast=2
phase 1, round 2: slow=2 fast=4
phase 1, round 3: slow=3 fast=6
phase 1, round 4: slow=4 fast=4
phase 2, start: p=0 slow=4
phase 2, round 1: p=1 slow=5
phase 2, round 2: p=2 slow=6
phase 2, round 3: p=3 slow=3
cycle starts at 3
```

Check with the formula: `a = 3`, `L = 4`. They met after 4 rounds at node `4`, which is `b = 1` step into the cycle; `a + b = 4 = 1 * L`. From node `4`, three steps (`5`, `6`, `3`) reach the start, and three steps from the head (`1`, `2`, `3`) reach it too.

## Code

```python
def detect_cycle(head):
    slow = fast = head
    while fast is not None and fast.next is not None:
        slow = slow.next
        fast = fast.next.next
        if slow is fast:                 # phase 1: they met inside the cycle
            p = head
            while p is not slow:         # phase 2: both move one step at a time
                p = p.next
                slow = slow.next
            return p                     # the first node of the cycle
    return None
```

## Complexity

`O(n)` time: phase 1 takes at most about `a + L` rounds, phase 2 exactly `a` rounds. `O(1)` extra memory.

## Another way

Store every visited node in a set and return the first node that is already in it. That is `O(n)` time and `O(n)` memory. With the length of the cycle `L` (problem 20) there is a third way: start two pointers at the head, move one of them `L` steps ahead, then move both one step at a time; they meet at the start of the cycle.
