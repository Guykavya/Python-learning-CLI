## Hint 1

To unlink a node you change the `next` of the node **before** it. So look one ahead: stand on `prev` and test `prev.next.val`. Where must `prev` start so that the head itself can be tested and removed?

## Hint 2

Two moves are possible on each step: unlink (`prev.next = prev.next.next`) or advance (`prev = prev.next`). Never both. Why must you not advance after an unlink? Try `[6, 6, 1]`.

## Hint 3

```
dummy = ListNode(0, head); prev = dummy
while prev.next is not None:
    if prev.next.val == target: prev.next = prev.next.next
    else: prev = prev.next
return dummy.next
```
