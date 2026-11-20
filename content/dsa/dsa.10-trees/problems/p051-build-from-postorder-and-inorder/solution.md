## Approach

Postorder is `left, right, root`, so reading it from the end gives the root, then the whole right subtree, then the whole left subtree (each read backwards in the same way). The inorder list splits the values around a root as before. So: take the next value from the end of the postorder as the root, find it in the inorder list through a dictionary, and build the **right** subtree first and the left subtree second.

## Code

```python
def build_from_in_post(inorder_vals, postorder_vals):
    index = {v: i for i, v in enumerate(inorder_vals)}
    next_root = iter(reversed(postorder_vals))    # roots from the end of the postorder

    def go(lo, hi):
        if lo > hi:
            return None
        val = next(next_root)
        node = TreeNode(val)
        mid = index[val]
        node.right = go(mid + 1, hi)              # the RIGHT subtree is built first
        node.left = go(lo, mid - 1)
        return node

    return go(0, len(inorder_vals) - 1)
```

## Complexity

`O(n)` time and `O(n)` memory for the dictionary, `O(h)` for the recursion.

## Another way

Mirror the preorder solution: reverse the postorder list, and you get "root, right, left", the preorder of the mirror image. Or slice: the left subtree has `mid` values, so `post[:mid]` is the left part and `post[mid:-1]` the right part (copies the lists, `O(n^2)` on a chain).
