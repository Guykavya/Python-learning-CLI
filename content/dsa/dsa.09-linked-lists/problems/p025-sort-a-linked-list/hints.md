## Hint 1

Base case: a list of 0 or 1 nodes is sorted. Otherwise you need the node at the end of the **first** half, so you can cut after it. Which start for `fast` makes `slow` stop on node 1 (not node 2) for a list of 2 nodes?

## Hint 2

`slow, fast = head, head.next`, then the usual loop. `second = slow.next`, then `slow.next = None` cuts. Now both halves are proper lists ending in `None`, each shorter than the whole.

## Hint 3

```
if head is None or head.next is None: return head
slow, fast = head, head.next
while fast and fast.next: slow = slow.next; fast = fast.next.next
second = slow.next; slow.next = None
return merge_two(sort_list(head), sort_list(second))
```
