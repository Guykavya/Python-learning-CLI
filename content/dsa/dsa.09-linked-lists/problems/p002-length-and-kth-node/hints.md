## Hint 1

For `length`: one counter, one walking variable. What is the loop condition that visits every node and then stops? Check it on the empty chain (`head is None`).

## Hint 2

For `get`: after zero steps you are on index 0 (the head); after one step on index 1. So take `k` steps. Before each step, ask: is there a node to step from?

## Hint 3

```
get(head, k):
    if k < 0: return None
    cur = head
    repeat k times:
        if cur is None: return None
        cur = cur.next
    return cur          # may be None if the list had exactly k nodes
```
