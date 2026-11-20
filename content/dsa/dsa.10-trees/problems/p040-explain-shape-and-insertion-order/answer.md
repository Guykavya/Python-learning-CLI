## Model answer

Inserting `1, 2, 3, 4, 5` in this order: every new key is larger than all the keys before it, so it goes to the **right** of the last node. The tree is a **chain** `1 -> 2 -> 3 -> 4 -> 5` of height 5. Inserting `3, 1, 5, 2, 4`: `3` is the root, `1` goes left, `5` goes right, `2` is larger than `1` so it becomes the right child of `1`, and `4` is smaller than `5`, so it becomes the left child of `5`. The tree is `[3, 1, 5, None, 2, 4]` and its height is 3.

Every sorted order (increasing or decreasing) gives a chain, because each key is larger (or smaller) than everything inserted before it, so it always walks the whole way down one side and becomes a new leaf at the end. With `n` sorted keys the height is `n`.

`search`, `insert` and `delete` each walk one path from the root, so their cost is `O(h)`, the height. For a chain `h = n`, and a search is as slow as scanning a linked list: `O(n)`. For a tree whose height is about `log2 n` they are `O(log n)`. So "a BST is `O(log n)`" is true only when the tree is reasonably balanced, and the insertion order decides that.

The inorder traversal of every tree in question 1 is `[1, 2, 3, 4, 5]`: inorder visits the left subtree (smaller keys), the node, and then the right subtree (larger keys), so it always gives the keys in sorted order, whatever the shape. The shape changes how long a path is; it does not change the order of the keys.

The smallest height for the keys `1` to `7` is 3 and comes from inserting the middle key first, then the middle of each half: for example `4, 2, 6, 1, 3, 5, 7` (a perfect tree). Keys in a random order give a height that is a small multiple of `log2 n`: the chapter measured a height of 19 for 500 random keys (against `log2 500`, about 9), and 500 for the same keys in sorted order.

A balanced tree (an AVL or a red-black tree) repairs the shape after every insert or delete with rotations, so the height stays near `log n` whatever the order of the keys.

Checklist: your answer should mention
- [ ] the sorted order gives a right chain `1 -> 2 -> 3 -> 4 -> 5` of height 5, and the other order gives `[3, 1, 5, None, 2, 4]` of height 3
- [ ] why a sorted order always gives a chain: each key is larger than everything before it
- [ ] the height of a chain of `n` keys is `n`
- [ ] the cost of each operation is the height, so a chain gives `O(n)`; a balanced shape gives `O(log n)`
- [ ] the inorder traversal is the sorted list of the keys for every insertion order
- [ ] the best order inserts the middle key first (`4, 2, 6, 1, 3, 5, 7`) and gives height 3
- [ ] random order gives a height of a small multiple of `log n` (the chapter: 19 for 500 keys)
- [ ] balanced trees keep the height near `log n` with rotations
