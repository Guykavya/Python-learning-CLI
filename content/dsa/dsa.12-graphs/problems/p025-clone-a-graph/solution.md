## Approach

A deep copy of a graph has two jobs: make one new node per old node, and rebuild every edge between the new nodes. The difficulty is cycles: when a walk comes back to a node it already copied, it must **reuse** that copy, not make a second one (and not loop forever). A dictionary `old node -> new node` solves both: it says whether a node was copied, and it gives the copy.

We walk the graph with BFS (chapter section 3). The first time we see a node we create its copy and queue it. When we take a node out, we fill its copy's neighbour list from the dictionary, in the original order. Self loops and repeated neighbours need nothing special: `copy_of[u]` exists already, so it is appended like any other neighbour.

```python
from collections import deque


def clone_graph(node):
    if node is None:
        return None
    copy_of = {node: Node(node.val)}
    queue = deque([node])
    while queue:
        u = queue.popleft()
        for v in u.neighbors:
            if v not in copy_of:
                copy_of[v] = Node(v.val)
                queue.append(v)
            copy_of[u].neighbors.append(copy_of[v])
    return copy_of[node]
```

Every node enters the queue once and every neighbour entry is handled once.

## Complexity

`O(V + E)` time, `O(V)` extra memory for the dictionary and the queue.

## Another way

A recursive DFS: `clone(u)` returns `copy_of[u]` if it exists; otherwise it creates the copy, stores it **before** recursing (otherwise a cycle recurses forever), and then appends `clone(v)` for each neighbour. It is shorter, but a chain of 20,000 nodes is 20,000 nested calls, far past Python's recursion limit (chapter section 4). An explicit stack instead of the queue works as well as BFS.
