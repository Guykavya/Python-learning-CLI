## Model answer

Three trees with the preorder `[1, 2, 3]`: `[1, 2, 3]` (2 is the left child and 3 the right child of 1), `[1, 2, None, 3]` (a left chain: 3 is the left child of 2), and `[1, None, 2, None, 3]` (a right chain). There are also `[1, 2, None, None, 3]` and `[1, None, 2, 3]`: five different trees in all, and every one of them is visited in the order 1, 2, 3.

A preorder list says **in which order** the nodes are visited, but it does not say where the left subtree **ends** and the right subtree begins. After the root, a left subtree can have any size: `2` may be the whole left subtree, and `3` the right subtree, or `2` and `3` may both be in the left subtree. The shape (which node is a child of which) is lost.

Two kinds of extra information make the tree unique. First, the **inorder** list of a tree with distinct values: for `[1, 2]` (2 on the left) the inorder is `[2, 1]`, for `[1, None, 2]` it is `[1, 2]`; the root is the first preorder item, and its position in the inorder list says which values are on the left and which on the right. Second, a **marker for every missing child**: the text of `[1, 2]` is `1,2,#,#,#` and of `[1, None, 2]` it is `1,#,2,#,#`. Now after every node exactly two subtrees follow, so no boundary is lost.

A BST needs only one traversal because of the order rule: every value in the left subtree is smaller than the node and every value in the right subtree is larger. In the preorder, after the root, the values smaller than the root come first (the left subtree) and the larger ones after them, so the rule (with lower and upper bounds) gives the boundary that the plain preorder misses.

With repeated values the inorder list cannot locate the root. For preorder `[1, 1]` and inorder `[1, 1]`, both the tree `[1, 1]` (a left child) and the tree `[1, None, 1]` (a right child) fit: the two lists are the same for different trees.

A tree with `n` nodes has `n + 1` empty child slots, because every node has two child slots and `n - 1` of the `2n` slots are filled by the other nodes: `2n - (n - 1) = n + 1`. The text has one token per node and one marker per empty slot, so `n + (n + 1) = 2n + 1` tokens.

Checklist: your answer should mention
- [ ] two (or three) different trees with the preorder `[1, 2, 3]`, written as level-order lists
- [ ] the preorder loses where the left subtree ends (the boundary between left and right)
- [ ] extra information 1: the inorder list (distinct values); extra information 2: markers for missing children
- [ ] the example `[1, 2]` and `[1, None, 2]`: same preorder, inorders `[2, 1]` and `[1, 2]`, texts `1,2,#,#,#` and `1,#,2,#,#`
- [ ] a BST needs one traversal because the order rule (smaller left, larger right, with bounds) gives the boundary
- [ ] repeated values break preorder + inorder (for example preorder `[1, 1]` and inorder `[1, 1]` fit two trees)
- [ ] `n` nodes have `n + 1` empty slots, so the serialisation has `2n + 1` tokens
