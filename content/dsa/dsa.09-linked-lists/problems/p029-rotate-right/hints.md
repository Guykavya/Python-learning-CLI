## Hint 1

First walk once to get the length `n` and the last node (`tail`). Then `k %= n`. If `k` is 0, nothing changes. How many nodes stay at the front, and which node is the last of them?

## Hint 2

The new tail is the node at index `n - k - 1` (0-based); walk `n - k - 1` steps from the head. The new head is `new_tail.next`. Then: `new_tail.next = None` and `tail.next = head`.

## Hint 3

```
if head is None or head.next is None: return head
n = 1; tail = head; while tail.next: tail = tail.next; n += 1
k %= n; if k == 0: return head
new_tail = head; repeat n-k-1 times: new_tail = new_tail.next
new_head = new_tail.next; new_tail.next = None; tail.next = head
return new_head
```
