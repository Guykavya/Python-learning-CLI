## Approach

Draw the tree after the inserts, then treat each delete on its own: find the node, name the case, change the picture, write the level-order list.

## Expected output

```text
start    : [50, 30, 70, 20, 40, 60, 80, None, None, 35, None, None, 65]
delete 40: [50, 30, 70, 20, 35, 60, 80, None, None, None, None, None, 65]
delete 70: [50, 30, 80, 20, 35, 60, None, None, None, None, None, None, 65]
delete 50: [60, 30, 80, 20, 35, 65]
inorder  : [20, 30, 35, 60, 65, 80]
```

## Why

| step | tree before | case | what happens |
|---|---|---|---|
| inserts | | | `35` goes under `40` (left), `65` under `60` (right) |
| delete 40 | `30` has `20` and `40` | one child (`35`) | the node is replaced by its left child, so `30.right` is `35` |
| delete 70 | `70` has `60` and `80` | two children | successor = smallest of the right subtree = `80`; copy `80` into the node; delete the old `80` (a leaf) |
| delete 50 | the root has `30` and `80` | two children | successor = leftmost of the right subtree = `60`; copy it into the root; delete the old `60`, which has only the right child `65`, so `65` replaces it as the left child of `80` |

After the last delete the root holds `60`. Its left subtree is `30` with `20` and `35`; its right subtree is `80` with the left child `65`. Every key on the left of `60` is smaller (`20, 30, 35`) and every key on the right is larger (`65, 80`).

The inorder line is sorted because delete only ever (a) removes a node whose place is taken by a subtree that is already in the right order, or (b) replaces a value by its neighbour in the sorted order, the successor, and removes that neighbour. A sorted inorder is the proof that the BST rule still holds. If a subtree were lost, or the successor stayed in the tree after being copied, the line would miss a key or show it twice.
