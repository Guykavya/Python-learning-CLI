## Approach

The first value of the preorder is the root. Its position in the inorder list splits the other values into the left subtree (before it) and the right subtree (after it). The preorder lists the whole left subtree first, then the whole right subtree, so if you take roots from the preorder one after another and build the **left** subtree first, each recursive call finds its own root next in line. A dictionary from value to inorder index finds the split in `O(1)`.

## Code

```python
def build_from_pre_in(preorder_vals, inorder_vals):
    index = {v: i for i, v in enumerate(inorder_vals)}
    next_root = iter(preorder_vals)               # hands out the roots in preorder

    def go(lo, hi):                               # build from inorder_vals[lo..hi]
        if lo > hi:
            return None
        val = next(next_root)                     # the next preorder item is this subtree's root
        node = TreeNode(val)
        mid = index[val]
        node.left = go(lo, mid - 1)               # left first: the preorder lists it first
        node.right = go(mid + 1, hi)
        return node

    return go(0, len(inorder_vals) - 1)
```

## Complexity

`O(n)` time: one call per node, with `O(1)` work each. `O(n)` memory for the dictionary and `O(h)` for the recursion.

## Another way

Slice the lists: `left_size = mid`, `left = build(pre[1:1 + left_size], ino[:mid])`, `right = build(pre[1 + left_size:], ino[mid + 1:])`. It is shorter, but each call copies lists, which makes it `O(n^2)` on a chain. For postorder + inorder (the next problem) read the postorder from the end and build the **right** subtree first.
