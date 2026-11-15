## Hint 1

The result is built like `from_list`: a dummy and a `tail`. At each step, which of the two front nodes goes after `tail`? After linking it, which pointer moves?

## Hint 2

For stability, take from `b` only if `b.val < a.val`; on a tie take from `a`. When the loop ends, one list is empty and the other is a sorted chain that is already linked: `tail.next = a or b` (written with `is not None`).

## Hint 3

```
dummy = ListNode(); tail = dummy
while a and b:
    if b.val < a.val: tail.next = b; b = b.next
    else: tail.next = a; a = a.next
    tail = tail.next
tail.next = a if a is not None else b
return dummy.next
```
