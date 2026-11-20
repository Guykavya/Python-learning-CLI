## Approach

Every path has a highest node. For a node `v`, the longest path whose highest node is `v` goes down the taller left branch and the taller right branch: its length in edges is `height(left) + height(right)` (heights in nodes). The diameter is the maximum of this number over all nodes. One recursive function can do all of it: it **returns** the height of its subtree (what the parent needs) and **records** `left + right` in a shared variable (what the answer needs).

## Code

```python
def diameter(root):
    best = 0

    def go(node):                                  # returns the height of the subtree (in nodes)
        nonlocal best
        if node is None:
            return 0
        left = go(node.left)
        right = go(node.right)
        best = max(best, left + right)             # the longest path with `node` as its highest point
        return 1 + max(left, right)                # what the parent needs

    go(root)
    return best
```

## Complexity

`O(n)` time, one visit per node. `O(h)` stack.

## Another way

Two BFS runs: start at any node, find the farthest node `a`; start again at `a` and find the farthest node from it; that distance is the diameter. It needs a graph with parent links (an undirected view of the tree), and it is the idea behind CSES "Tree Diameter" with 2*10^5 nodes, where recursion is not allowed. A brute force that runs BFS from every node is `O(n^2)` and good for testing.
