## Approach

Draw the tree, then write each list one subtree at a time: preorder = node + left + right, inorder = left + node + right, postorder = left + right + node.

## Expected output

```text
preorder [1, 2, 4, 7, 3, 5, 6]
inorder [4, 7, 2, 1, 5, 3, 6]
postorder [7, 4, 2, 5, 6, 3, 1]
```

## Why

The list `[1, 2, 3, 4, None, 5, 6, None, 7]` builds this tree (the queue gives `2` and `3` to `1`; `4` and a gap to `2`; `5` and `6` to `3`; a gap and `7` to `4`):

```text
1
|-- left  2
|     |-- left  4
|           |-- right 7
|-- right 3
      |-- left  5
      |-- right 6
```

| subtree | preorder | inorder | postorder |
|---|---|---|---|
| `4` (right child `7`) | `4, 7` | `4, 7` | `7, 4` |
| `2` (left subtree `4...`) | `2, 4, 7` | `4, 7, 2` | `7, 4, 2` |
| `3` (leaves `5`, `6`) | `3, 5, 6` | `5, 3, 6` | `5, 6, 3` |
| `1` (whole tree) | `1, 2, 4, 7, 3, 5, 6` | `4, 7, 2, 1, 5, 3, 6` | `7, 4, 2, 5, 6, 3, 1` |

The root is first in the preorder and last in the postorder. In the inorder it sits between the two subtrees (`4, 7, 2` on its left, `5, 3, 6` on its right), which is how a tree can be rebuilt from two of the lists (chapter section 11).
