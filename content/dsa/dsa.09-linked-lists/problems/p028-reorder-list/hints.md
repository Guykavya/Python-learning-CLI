## Hint 1

Three steps you already know: the end of the first half (`slow, fast = head, head.next`), the in-place reversal of the second half, and a merge-like walk over two lists. Which of the two halves may be one node longer?

## Hint 2

Weave with `first = head` and `second` = head of the reversed half. Each round: save `n1 = first.next` and `n2 = second.next`, then `first.next = second`, `second.next = n1`, and move on to `n1`, `n2`. Stop when `second` is `None`.

## Hint 3

```
slow, fast = head, head.next; loop; second = slow.next; slow.next = None
second = reverse(second)
first = head
while second:
    n1 = first.next; n2 = second.next
    first.next = second; second.next = n1
    first = n1; second = n2
```
