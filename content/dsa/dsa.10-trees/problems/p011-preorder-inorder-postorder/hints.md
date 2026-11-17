## Hint 1

Finish the sentence for `inorder`: "`inorder(node)` returns the list of values of the tree starting at `node`, in inorder". If you have the inorder list of the left subtree and of the right subtree, how do you get the list for `node`?

## Hint 2

Join three lists: the left list, then `[node.val]`, then the right list. For preorder put `[node.val]` first, for postorder last. The empty tree gives `[]`, which is the neutral element of list joining.

## Hint 3

```
def inorder(root):
    if root is None: return []
    return inorder(root.left) + [root.val] + inorder(root.right)
```
(or: an inner helper that appends to one list created in the outer function)
