## Approach

Both problems walk two trees (or two subtrees of one tree) in step. The three cases are always the same: two empty trees match; one empty and one not do not match; two nodes match when their values are equal and their children match. For `same_tree` the children are compared left with left and right with right. For the mirror image they are compared **crosswise**: the left child of one with the right child of the other. A tree is symmetric when its left subtree is the mirror of its right subtree.

## Code

```python
def same_tree(a, b):
    if a is None and b is None:
        return True
    if a is None or b is None:
        return False
    return a.val == b.val and same_tree(a.left, b.left) and same_tree(a.right, b.right)


def is_mirror(a, b):
    if a is None and b is None:
        return True
    if a is None or b is None:
        return False
    return a.val == b.val and is_mirror(a.left, b.right) and is_mirror(a.right, b.left)


def is_symmetric(root):
    return root is None or is_mirror(root.left, root.right)
```

## Complexity

`O(n)` time (at most one visit per node of the smaller tree) and `O(h)` memory for the recursion.

## Another way

Compare the level-order lists with `None` for gaps (`to_level(a) == to_level(b)`): it is a different representation of the same information, and the tests use it as the brute force. Iterative versions put pairs of nodes on a stack or in a queue. A symmetric tree is also a tree that is equal to its own mirror copy: `same_tree(root, invert(root))` after a copy.
