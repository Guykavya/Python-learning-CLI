## Approach

Draw before you explain: list the trees that can be visited as `1, 2, 3` in preorder, then see what a second list (inorder) or a marker for each missing child adds.

## Model answer

See `answer.md`.

## What to check

- You gave **different** trees for the same preorder, as level-order lists, and checked each by writing its preorder.
- You named the lost information: the end of the left subtree.
- You gave **two** kinds of fix and showed both on `[1, 2]` and `[1, None, 2]`.
- You said why a BST is special (the order rule) and why repeated values break the inorder method.
- You explained the `2n + 1` count with `n + 1` empty slots.

## Another way

Check your five trees with code: build each from its level-order list with `build_tree` (section 2) and print its preorder with the recursive `preorder` of section 4. Then print the inorder of each: they are all different, because for distinct values the pair (preorder, inorder) determines the tree.
