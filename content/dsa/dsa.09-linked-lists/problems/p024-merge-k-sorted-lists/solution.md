## Approach

The next node of the result is always the smallest of the `k` current front nodes. A min-heap of those fronts gives it in `O(log k)`. After taking a node, its successor becomes the new front of that list and goes into the heap. The tuple `(value, list index, node)` sorts by value; on equal values the indexes differ, so Python never has to compare two nodes.

## Code

```python
import heapq


def merge_k(lists):
    heap = []
    for i, node in enumerate(lists):
        if node is not None:
            heap.append((node.val, i, node))     # i breaks ties: nodes are never compared
    heapq.heapify(heap)
    dummy = ListNode()
    tail = dummy
    while heap:
        _, i, node = heapq.heappop(heap)
        tail.next = node
        tail = node
        if node.next is not None:
            heapq.heappush(heap, (node.next.val, i, node.next))
    tail.next = None
    return dummy.next
```

(`tail.next = None` is not strictly needed, because the last node popped is the end of its own list, but it makes the end explicit.)

## Complexity

Each of the `N` nodes is pushed and popped once; the heap holds at most `k` entries, so each operation is `O(log k)`: `O(N log k)` time, `O(k)` extra memory for the heap.

## Another way

Divide and conquer with `merge_two` (problem 23):

```python
def merge_k(lists):
    lists = [h for h in lists if h is not None]
    if not lists:
        return None
    while len(lists) > 1:
        merged = []
        for i in range(0, len(lists), 2):
            if i + 1 < len(lists):
                merged.append(merge_two(lists[i], lists[i + 1]))
            else:
                merged.append(lists[i])
        lists = merged
    return lists[0]
```

Each round halves the number of lists and walks every node once: `log k` rounds of `O(N)`, the same `O(N log k)`, with only `O(k)` memory for the list of heads. Merging one by one (`result = merge_two(result, next_list)`) is `O(k N)` and too slow for the big test.
