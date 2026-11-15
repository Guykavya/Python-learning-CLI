## Approach

Build the tree on paper and run `heapify` from the last parent to the root. A value sinks until it is not smaller than its children.

## Expected output

```text
start 2
swap index 2 with 5 [3, 9, 5, 1, 4, 2]
start 1
start 0
swap index 0 with 1 [9, 3, 5, 1, 4, 2]
swap index 1 with 4 [9, 4, 5, 1, 3, 2]
[9, 4, 5, 1, 3, 2]
```

## Why

Leaves are already one-element heaps, so only the first half of the list needs a sift. Most nodes are low in the tree and sink only a few steps, which is why the total work of building a heap is `O(n)`. The final list `[9, 4, 5, 1, 3, 2]` satisfies the heap rule: 9 >= 4, 5; 4 >= 1, 3; 5 >= 2.
