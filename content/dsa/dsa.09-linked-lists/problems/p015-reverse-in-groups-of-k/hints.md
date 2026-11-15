## Hint 1

Keep a variable `group_prev`: the node just **before** the next group (start: a dummy). From it, try to step `k` times. If you hit `None` on the way, the group is incomplete and you are done. Otherwise you now hold `kth`, the last node of the group.

## Hint 2

Reverse the group with the three-variable loop, but start `prev` at `kth.next` (the node after the group) instead of `None`. Then the reversed group's last node already points at the rest. What is left to connect?

## Hint 3

```
dummy = ListNode(0, head); group_prev = dummy
loop:
    kth = group_prev; step k times (return dummy.next if None)
    group_next = kth.next
    prev = group_next; cur = group_prev.next
    while cur is not group_next: nxt = cur.next; cur.next = prev; prev = cur; cur = nxt
    first = group_prev.next          # old first, now last of the group
    group_prev.next = kth            # kth is the new first
    group_prev = first
```
