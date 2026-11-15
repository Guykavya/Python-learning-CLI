## Hint 1

Put a dummy in front and walk `left - 1` steps from it: you stand on the node **before** the range (the dummy itself when `left = 1`). Remember it as `before`, and remember `first = before.next`. Which of the two will point where at the end?

## Hint 2

Reverse exactly `right - left + 1` nodes with the three-variable loop, starting with `prev = None, cur = first`. When the loop ends, `prev` is the new first node of the range and `cur` is the node **after** the range.

## Hint 3

```
dummy = ListNode(0, head); before = dummy
repeat left-1 times: before = before.next
first = before.next; prev = None; cur = first
repeat right-left+1 times: nxt = cur.next; cur.next = prev; prev = cur; cur = nxt
before.next = prev
first.next = cur
return dummy.next
```
