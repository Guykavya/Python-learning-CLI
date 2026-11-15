## Hint 1

Start both pointers on a dummy before the head. If `fast` is exactly `n` nodes ahead of `slow`, where is `slow` when `fast` is on the **last** node?

## Hint 2

Move `fast` `n` times. Then, while `fast.next` exists, move both. Now `slow.next` is the node to remove: `slow.next = slow.next.next`. Return `dummy.next` (the head may have been removed).

## Hint 3

```
dummy = ListNode(0, head); fast = slow = dummy
repeat n times: fast = fast.next
while fast.next: fast = fast.next; slow = slow.next
slow.next = slow.next.next
return dummy.next
```
