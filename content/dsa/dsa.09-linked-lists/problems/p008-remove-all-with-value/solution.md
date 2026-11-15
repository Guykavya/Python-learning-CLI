## Approach

Put a dummy node before the head, so every real node has a node before it. Stand on `prev` (starting at the dummy) and look at `prev.next`:

- if it matches, unlink it by skipping it: `prev.next = prev.next.next`. Stay where you are, because the new `prev.next` has not been checked yet;
- otherwise move forward.

The head of the result is `dummy.next`, which is right even if the old head was removed, and is `None` if every node was removed.

## Code

```python
def remove_all(head, target):
    dummy = ListNode(0, head)
    prev = dummy
    while prev.next is not None:
        if prev.next.val == target:
            prev.next = prev.next.next      # unlink; do NOT move prev
        else:
            prev = prev.next
    return dummy.next
```

## Complexity

`O(n)` time: every step either removes a node or moves past one. `O(1)` extra memory (one dummy node).

## Another way

Without a dummy: first skip the matches at the front with `while head is not None and head.val == target: head = head.next`, then run the same loop from `head`. It works, but it is two loops for one idea. A third way builds a new chain by linking the kept nodes after a `tail` (like `from_list`, but with existing nodes), and finally sets `tail.next = None`.
