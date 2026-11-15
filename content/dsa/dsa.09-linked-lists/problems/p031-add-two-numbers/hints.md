## Hint 1

On paper you add the ones digits first, then the tens, carrying 1 when a column reaches 10. The heads are the ones digits, so walk both lists from the head together. What do you add in a column where one list has already ended?

## Hint 2

`total = carry + (a.val if a else 0) + (b.val if b else 0)`, then `carry, digit = divmod(total, 10)`. Link a new node with `digit` after a `tail`, like `from_list`. The loop continues while `a`, `b` or `carry` is left.

## Hint 3

```
dummy = ListNode(); tail = dummy; carry = 0
while a or b or carry:
    total = carry
    if a: total += a.val; a = a.next
    if b: total += b.val; b = b.next
    carry, digit = divmod(total, 10)
    tail.next = ListNode(digit); tail = tail.next
return dummy.next
```
