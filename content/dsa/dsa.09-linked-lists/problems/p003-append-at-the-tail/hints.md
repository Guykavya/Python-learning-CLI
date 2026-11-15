## Hint 1

Which node's `next` must change? Draw `1 -> 2 -> 3 -> None` and point at it. What is true about that node that is true about no other node?

## Hint 2

`while cur is not None` walks **off** the end; you need to stop one node earlier: `while cur.next is not None`. That condition crashes on an empty list, so handle `head is None` first.

## Hint 3

```
node = new node(val)
if head is None: return node
cur = head
while cur.next is not None: cur = cur.next
cur.next = node
return head
```
