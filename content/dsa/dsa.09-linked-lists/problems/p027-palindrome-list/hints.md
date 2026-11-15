## Hint 1

Use `slow, fast = head, head.next` and the usual loop: `slow` stops at the end of the first half (for odd lengths, on the middle node). The second half starts at `slow.next`. Reverse it with `reverse_list`.

## Hint 2

Walk `a` from `head` and `b` from the reversed second half while `b` exists, comparing values. Store the answer in a variable instead of returning at the first mismatch. Then `slow.next = reverse_list(second)` puts the list back.

## Hint 3

```
if head is None or head.next is None: return True
slow, fast = head, head.next
while fast and fast.next: slow = slow.next; fast = fast.next.next
second = reverse_list(slow.next)
result = True; a, b = head, second
while b: if a.val != b.val: result = False; break; a = a.next; b = b.next
slow.next = reverse_list(second)
return result
```
