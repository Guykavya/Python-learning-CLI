## Hint 1

The tree is: `1` with left child `2` and right child `3`; `2` has the left child `4` and no right child; `4` has no left child and the right child `7`; `3` has the children `5` and `6`. Write the preorder first: the node, then everything on the left, then everything on the right.

## Hint 2

For the inorder write the left subtree of the root first: it is the subtree of `2`, whose own left subtree is the subtree of `4` (which has only a right child, `7`), so the inorder of that subtree is `4, 7`, then `2`. Then the root `1`, then the subtree of `3`: `5, 3, 6`. For the postorder every node comes after its children: `7, 4, 2`, then `5, 6, 3`, then `1`.
