## Approach

Work group by group with a pointer `group_prev` to the node before the current group (initially a dummy).

1. **Check** the group: step `k` times from `group_prev`. Reaching `None` means fewer than `k` nodes are left; they stay as they are, so return `dummy.next`.
2. **Reverse** the group with the three-variable loop, starting `prev` at `group_next = kth.next`. That way the old first node of the group, which becomes its last, ends up pointing at the rest of the list.
3. **Connect** the front: `group_prev.next = kth` (the old last node is the new first).
4. **Advance**: the old first node is now the last node of this group, so it is the node before the next group.

## Code

```python
def reverse_k_group(head, k):
    dummy = ListNode(0, head)
    group_prev = dummy                       # the node before the current group
    while True:
        kth = group_prev                     # find the k-th node of the group
        for _ in range(k):
            kth = kth.next
            if kth is None:
                return dummy.next            # fewer than k nodes left: keep them
        group_next = kth.next
        prev, cur = group_next, group_prev.next
        while cur is not group_next:         # reverse the group, its end points at group_next
            nxt = cur.next
            cur.next = prev
            prev = cur
            cur = nxt
        first = group_prev.next              # the old first node is now the group's last
        group_prev.next = kth
        group_prev = first
```

## Complexity

`O(n)` time: every node is visited at most twice (once while checking, once while reversing). `O(1)` extra memory.

## Another way

Recursively: check that `k` nodes exist, reverse them, and set the old first node's `next` to `reverse_k_group(rest, k)`. It is shorter, but uses one stack frame per **group**, so for `k = 1` and long lists it hits the recursion limit. Another simple way: count the length `n` first, then do `n // k` rounds of "reverse the next k nodes".
