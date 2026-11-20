## Hint 1

Take `[1, 2, 5, 3, 4, None, 6]`. The preorder is `1, 2, 3, 4, 5, 6`. After `1` come all the nodes of its left subtree (`2, 3, 4`), and only then the right subtree (`5, 6`). So the old right subtree must hang **after the last node of the left subtree**. Which node is that last node?

## Hint 2

The last node of the preorder of a subtree is found by going right as far as you can (and the subtree's last node has no right child). Loop over the nodes: if `cur` has a left child, find the rightmost node `last` of the left subtree, set `last.right = cur.right`, then `cur.right = cur.left` and `cur.left = None`. Move to `cur.right` and repeat. In the other case just move on.

## Hint 3

```
cur = root
while cur is not None:
    if cur.left is not None:
        last = cur.left
        while last.right is not None: last = last.right
        last.right = cur.right        # the old right subtree goes after the left subtree
        cur.right = cur.left          # the left subtree moves to the right
        cur.left = None
    cur = cur.right
```
