## Approach

Walk down from the root. At a node larger than `key`, the node is a **candidate** for the successor, and a smaller candidate can only be in its left subtree, so remember the node and go left. At a node smaller than or equal to `key`, every value in its left subtree is too small, so go right. The last candidate remembered is the smallest value larger than `key`. This covers both cases: a node with a right subtree finds its successor inside it, and a node without one finds it among the ancestors where the walk turned left.

## Code

```python
def successor(root, key):
    best = None
    cur = root
    while cur is not None:
        if key < cur.val:
            best = cur                  # a possible answer; look for a smaller one on the left
            cur = cur.left
        else:
            cur = cur.right             # key >= cur.val: the answer must be larger
    return best.val if best is not None else None
```

## Complexity

`O(h)` time (one walk down) and `O(1)` extra memory: no stack, no parent pointers.

## Another way

Two separate cases: if the node has a right subtree, the successor is the leftmost node of that subtree; otherwise it is the lowest ancestor whose left subtree contains the node, which you find by walking down from the root and remembering the last node where you turned left. The single loop above does both in one walk. With **parent pointers** you can go up instead; with an inorder list and `bisect` you can answer it in `O(log n)` after an `O(n)` build.
