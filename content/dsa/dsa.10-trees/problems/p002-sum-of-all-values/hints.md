## Hint 1

Finish the sentence: "`tree_sum(node)` returns the sum of the values in the tree that starts at `node`". What is the sum of an empty tree? If you know the sums of the left and right trees, what do you add to get the sum for `node`?

## Hint 2

The node's own value plus the two subtree sums. Negative values need no special case: adding a negative number is just subtraction.

## Hint 3

```
if root is None: return 0
return root.val + tree_sum(root.left) + tree_sum(root.right)
```
