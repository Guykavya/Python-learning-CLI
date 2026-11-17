## Approach

The path between `p` and `q` goes up from `p` to their lowest common ancestor and then down to `q`, so its length in edges is `depth(p) - depth(a) + depth(q) - depth(a)` where `a` is the LCA. Find the LCA with the recursion of problem 47. Find the depths with a parent map (a dictionary filled by a loop) and by counting the steps up to the root.

## Code

```python
def distance(root, p, q):
    parent = {root: None}
    stack = [root]
    while stack:                                  # a parent map, filled with a loop
        node = stack.pop()
        for child in (node.left, node.right):
            if child is not None:
                parent[child] = node
                stack.append(child)

    def depth(node):
        steps = 0
        while parent[node] is not None:
            node = parent[node]
            steps += 1
        return steps

    def lca(node):
        if node is None or node is p or node is q:
            return node
        left, right = lca(node.left), lca(node.right)
        if left is not None and right is not None:
            return node
        return left if left is not None else right

    ancestor = lca(root)
    return depth(p) + depth(q) - 2 * depth(ancestor)
```

## Complexity

`O(n)` time (the parent map, the LCA, and three walks up of at most `h` steps) and `O(n)` memory for the map.

## Another way

One recursion can return the depth where it found `p` or `q` and report the distance when both sides found one, without a parent map. Or treat the tree as an undirected graph and run a breadth-first search from `p` until `q` is reached: that is the brute force used in the tests, and it needs no LCA at all.
