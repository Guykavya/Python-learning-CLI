## Hint 1

If `fast` moves twice as fast as `slow`, where is `slow` when `fast` has walked the whole list?

## Hint 2

`fast` can take two steps only if `fast` exists and `fast.next` exists. Use exactly that as the loop condition. Check with 1, 2, 3 and 4 nodes which node `slow` ends on.

## Hint 3

```
slow = fast = head
while fast is not None and fast.next is not None:
    slow = slow.next; fast = fast.next.next
return slow
```
