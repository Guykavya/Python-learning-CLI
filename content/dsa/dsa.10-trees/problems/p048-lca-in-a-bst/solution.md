## Approach

In a BST, if both values are smaller than the current node, both nodes are in its left subtree, so the LCA is there too; if both are larger, it is in the right subtree. At the first node where this is not true (the values are on different sides, or one of them equals the node) the paths to `p` and `q` split, and that node is the LCA. A loop from the root down does it with no recursion.

## Code

```python
def lca_bst(root, p, q):
    cur = root
    while cur is not None:
        if p.val < cur.val and q.val < cur.val:
            cur = cur.left
        elif p.val > cur.val and q.val > cur.val:
            cur = cur.right
        else:
            return cur                       # the values split here (or one equals this node)
    return None
```

## Complexity

`O(h)` time (one walk down) and `O(1)` extra memory.

## Another way

The general algorithm of problem 47 works on any binary tree, including a BST, but costs `O(n)`. With parent pointers, you can also go up from both nodes (the intersection of two linked lists of dsa.09). The BST version is the same idea as a binary search: each comparison throws away a whole subtree.
