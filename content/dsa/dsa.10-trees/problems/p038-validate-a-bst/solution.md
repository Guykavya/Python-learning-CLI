## Approach

Every node must lie strictly between a lower and an upper bound that come from its **ancestors**. The root has no bounds. Going left from a node with value `v` makes `v` the new upper bound; going right makes it the new lower bound. A node outside its bounds breaks the rule at some ancestor, and the function returns `False`. `None` stands for "no bound yet", so no tree value can collide with a sentinel.

## Code

```python
def is_valid_bst(root):
    def check(node, lo, hi):
        if node is None:
            return True
        if lo is not None and node.val <= lo:
            return False
        if hi is not None and node.val >= hi:
            return False
        return check(node.left, lo, node.val) and check(node.right, node.val, hi)

    return check(root, None, None)
```

## Complexity

`O(n)` time (each node is checked once) and `O(h)` memory for the recursion.

## Another way

A tree is a BST exactly when its **inorder** traversal is strictly increasing. Walk the tree inorder with the iterative stack of section 5 and compare each value with the previous one, stopping at the first violation. It uses a loop instead of recursion, so it also works on very deep chains.
