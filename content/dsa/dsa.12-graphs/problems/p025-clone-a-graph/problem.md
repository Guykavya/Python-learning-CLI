# Clone a graph

A graph is given as objects: each vertex is a `Node` with a value `val` and a list `neighbors` of other `Node` objects. The class is in `starter.py` (keep it as it is):

```python
class Node:
    def __init__(self, val=0, neighbors=None):
        self.val = val
        self.neighbors = neighbors if neighbors is not None else []
```

Write `clone_graph(node)`. It returns a **deep copy** of the part of the graph that can be reached from `node`: a brand new `Node` for every reachable vertex, with the same `val`, and with `neighbors` lists that point to the **new** nodes, in the **same order** as in the original.

Rules:

- `clone_graph(None)` returns `None`.
- No new node may be an old node, and no new `neighbors` list may contain an old node.
- The graph can have cycles, self loops (a node in its own `neighbors`) and the same neighbour listed twice. The copy must have exactly the same shape: if `a.neighbors` is `[b, b, a]`, the copy's list is `[b', b', a']`.
- Values are not always unique: two different nodes can both have `val == 7`. Do not identify nodes by their value.
- The original graph must not be changed.
- A graph can be a chain of 20,000 nodes: a recursive copy hits the recursion limit, so use a queue or a stack.

## Example

```python
>>> a, b, c = Node(1), Node(2), Node(3)
>>> a.neighbors = [b, c]; b.neighbors = [a, c]; c.neighbors = [a, b]   # a triangle
>>> a2 = clone_graph(a)
>>> a2 is a, a2.val, [n.val for n in a2.neighbors]
(False, 1, [2, 3])
>>> a2.neighbors[0].neighbors[0] is a2          # the copy of b points back to the copy of a
True
```

## Constraints

- Up to `2 * 10**4` nodes and `10**5` neighbour entries. `O(V + E)` time.

## Think about

When you reach a node for the second time (a cycle), how do you find the copy you already made of it? Why must that lookup use the node object and not its value?
