## Hint 1

The smallest node of all is one of the `k` front nodes. If you keep the `k` fronts in a min-heap, how do you get the smallest one, and which node replaces it in the heap?

## Hint 2

Push tuples `(node.val, i, node)`, where `i` is the index of the list. When you pop `(val, i, node)`, link `node` after `tail` and push `node.next` (if any) with the same `i`. The index makes every tuple unique before the node is reached, so nodes are never compared.

## Hint 3

```
heap = [(h.val, i, h) for i, h in enumerate(lists) if h]; heapify(heap)
dummy = ListNode(); tail = dummy
while heap:
    _, i, node = heappop(heap)
    tail.next = node; tail = node
    if node.next: heappush(heap, (node.next.val, i, node.next))
return dummy.next
```
