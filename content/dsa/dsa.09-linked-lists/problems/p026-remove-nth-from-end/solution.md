## Approach

Keep a gap of exactly `n` nodes between two pointers that start on a dummy. When `fast` stands on the last node, `slow` is `n` nodes behind it, so `slow.next` is the `n`-th node from the end. Unlink it. The dummy gives the head a node before it, which is needed when `n` equals the length.

Check with `[1, 2, 3, 4, 5]`, `n = 2`: `fast` goes 2 ahead to node `2`; then both move until `fast` is on `5`: `slow` is on `3`, and `slow.next` is `4`, the second from the end.

## Code

```python
def remove_nth_from_end(head, n):
    dummy = ListNode(0, head)
    fast = slow = dummy
    for _ in range(n):                   # fast goes n nodes ahead
        fast = fast.next
    while fast.next is not None:         # keep the gap until fast is on the last node
        fast = fast.next
        slow = slow.next
    slow.next = slow.next.next           # slow is just before the node to remove
    return dummy.next
```

## Complexity

`O(L)` time in one pass (`fast` walks the list once, `slow` follows), `O(1)` extra memory.

## Another way

Two passes: count the length `L`, then remove the node at index `L - n` (walk `L - n` steps from the dummy). Same `O(L)` time, simpler to get right, but it walks the list twice. The gap technique is worth knowing because it also answers "give me the `k`-th node from the end" in one pass on a stream that you cannot walk twice.
