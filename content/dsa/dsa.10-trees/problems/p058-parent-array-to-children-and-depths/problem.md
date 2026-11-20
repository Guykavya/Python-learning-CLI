# Parent array to children lists and depths

Chapter section 13: a tree can arrive as a list `parent` where `parent[i]` is the parent of node `i`, and the root has `parent[i] == -1`. The nodes are numbered `0` to `n - 1`. There is exactly one root and `n >= 1`. Write `children_and_depths(parent)` that returns a pair `(children, depth)`:

- `children[i]` is the list of the children of node `i`, in **increasing order of their numbers** (an empty list for a leaf);
- `depth[i]` is the number of **edges** from the root to node `i` (the root has depth `0`).

**Careful:** the parent of a node can have a **larger** number than the node itself. And the tree can be a path of 5,000 nodes, so no recursion: use a loop and a queue (or a stack).

## Example

```python
>>> children, depth = children_and_depths([-1, 0, 0, 1, 1, 2])
>>> children
[[1, 2], [3, 4], [5], [], [], []]
>>> depth
[0, 1, 1, 2, 2, 2]
>>> children_and_depths([1, -1])               # node 1 is the root; node 0 is its child
([[], [0]], [1, 0])
>>> children_and_depths([-1])
([[]], [0])
```

## Constraints

- Up to 5,000 nodes, any shape (also a path). `O(n)` time.

## Think about

How do you find the root? Why can you **not** compute `depth[i] = depth[parent[i]] + 1` in one pass from `0` to `n - 1`? Which traversal gives every node its depth after its parent's depth?
