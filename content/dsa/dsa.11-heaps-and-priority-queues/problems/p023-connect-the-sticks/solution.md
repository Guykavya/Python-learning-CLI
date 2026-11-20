## Approach

Think of the joins as a tree: the sticks are leaves, every join creates a parent whose length is the sum of its two children. A stick's length is paid once for every join on the path from its leaf to the root, so long sticks should be near the root (joined last) and short sticks deep in the tree (joined first). The greedy rule "join the two shortest sticks" does exactly that, and it is optimal. This is the same idea as **Huffman coding**.

A min-heap gives the two shortest sticks in `O(log n)`, and the new stick goes back in with a push.

## Code

```python
import heapq

def connect_sticks(sticks):
    heap = list(sticks)                  # a copy: heapify would reorder the caller's list
    heapq.heapify(heap)
    cost = 0
    while len(heap) > 1:
        a = heapq.heappop(heap)
        b = heapq.heappop(heap)
        cost += a + b
        heapq.heappush(heap, a + b)
    return cost
```

## Complexity

`O(n log n)` time (`n - 1` rounds of two pops and one push on a heap of at most `n` items), `O(n)` memory for the copy.

## Another way

- Keep a **sorted list** and insert the new stick with `bisect.insort`: each round moves up to `n` items, `O(n^2)` in the worst case, but the move is fast in practice.
- Sort once and use **two queues**: the sorted original sticks and a queue of the new sticks. New sticks are created in nondecreasing order, so the queue stays sorted, and each round takes the two smallest fronts of the two queues: `O(n)` after the sort.
- To check yourself, write the brute force that tries every pair to join at every step (only for 5 or 6 sticks): the greedy answer must match it.
