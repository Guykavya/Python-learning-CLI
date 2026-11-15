## Hint 1

Keep a counter `index` next to the walking variable `cur`. When `cur` moves one node, by how much must `index` change?

## Hint 2

Return **as soon as** you see the target: that gives the first match. If the loop ends without returning, nothing matched.

## Hint 3

```
index = 0; cur = head
while cur is not None:
    if cur.val == target: return index
    index += 1; cur = cur.next
return -1
```
