## Approach

Build the child lists in one pass over the array: for every node that has a parent, append the node to its parent's list. Going through the nodes in increasing order keeps each list sorted. The root is the node with parent `-1`. Depths cannot be computed in array order, because the parent of a node may come later in the array, so run a breadth-first search from the root: a node is taken from the queue only after its parent set its depth, so `depth[child] = depth[node] + 1` is always based on a known value.

## Code

```python
from collections import deque


def children_and_depths(parent):
    n = len(parent)
    children = [[] for _ in range(n)]
    root = -1
    for node, p in enumerate(parent):
        if p == -1:
            root = node
        else:
            children[p].append(node)                 # going upwards keeps every list sorted
    depth = [0] * n
    queue = deque([root])
    while queue:                                     # every node is reached after its parent
        node = queue.popleft()
        for c in children[node]:
            depth[c] = depth[node] + 1
            queue.append(c)
    return children, depth
```

## Complexity

`O(n)` time (one pass for the children, one visit per node in the search) and `O(n)` memory for the lists and the queue. No recursion, so a path of any length works.

## Another way

For each node, climb the parent links to the root and count the steps: `O(n * depth)`, so `O(n^2)` on a path. It is the brute force the tests use for random trees. With memoisation (store each depth once found) it is `O(n)` again. A depth-first search with an explicit stack also works.
