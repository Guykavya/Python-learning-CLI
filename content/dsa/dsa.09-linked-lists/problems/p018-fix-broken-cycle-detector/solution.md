## Approach

Once `fast` enters a cycle, it stays inside the cycle forever. If the cycle does not contain the head, `fast is head` can never be true, and nothing else stops the loop, so it runs forever. The classmate's test lists all had the head in the cycle (or no cycle), which is why the bug hid.

The correct test compares the two pointers: inside the cycle the distance from `slow` to `fast` shrinks by one node per round, so they must land on the same node. That works wherever the cycle starts.

## Code

```python
def has_cycle(head):
    slow = head
    fast = head
    while fast is not None and fast.next is not None:
        slow = slow.next
        fast = fast.next.next
        if slow is fast:             # was: fast is head
            return True
    return False
```

Trace on `1 -> 2 -> 3 -> 2 ...`: after round 1, `slow` = 2 and `fast` = 3; after round 2, both are on node 3, so the function returns `True`.

## Complexity

`O(n)` time, `O(1)` memory, as before.

## Another way

A "smallest change" that keeps the idea "come back to a known node" also exists (Brent's method): remember a node `power` steps in, move one pointer, and every time the step count doubles, move the remembered node to the current one. It also finds cycles that do not contain the head. Floyd's two pointers are simpler and are what the chapter uses.
