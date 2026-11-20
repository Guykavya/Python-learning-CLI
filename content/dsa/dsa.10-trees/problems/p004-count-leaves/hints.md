## Hint 1

If your only base case is `None -> 0`, where does a `1` ever come from? The recursion ends in `None` calls, which all return 0. So something must produce a 1 before the recursion reaches `None`. Which kind of node is it?

## Hint 2

Add a second base case: a node with no left child and no right child returns 1. For every other node, the leaves of the tree are the leaves of the left subtree plus the leaves of the right subtree.

## Hint 3

```
if root is None: return 0
if root.left is None and root.right is None: return 1
return count_leaves(root.left) + count_leaves(root.right)
```
