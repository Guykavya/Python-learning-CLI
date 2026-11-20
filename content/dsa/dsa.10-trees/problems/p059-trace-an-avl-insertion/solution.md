## Approach

Insert like in a plain BST, then walk **up** the path and fix the first node whose balance factor is `2` or `-2`. Draw the tree after every key.

## Expected output

```text
insert 10: [10]
insert 20: [10, None, 20]
rotate_left at 10
insert 30: [20, 10, 30]
insert 40: [20, 10, 30, None, None, None, 40]
rotate_left at 30
insert 50: [20, 10, 40, None, None, 30, 50]
rotate_right at 40
rotate_left at 20
insert 25: [30, 20, 40, 10, 25, None, 50]
height: 3
```

## Why

| key | where it lands | first unbalanced node (going up) | case | fix |
|---|---|---|---|---|
| 10 | root | none | | |
| 20 | right of 10 | none (`10` has factor `-1`) | | |
| 30 | right of 20 | `10`, factor `-2` | right-right (child `20` has factor `-1`) | left rotation at `10`: `20` on top |
| 40 | right of 30 | none | | |
| 50 | right of 40 | `30`, factor `-2` | right-right (child `40` has factor `-1`) | left rotation at `30`: `40` on top of `30` and `50` |
| 25 | left of 30 | `20`, factor `-2` (left height 1, right height 3) | right-left (child `40` has factor `+1`) | right rotation at `40`, then left rotation at `20` |

After `25` the tree is `30` at the top with the left subtree `20` (children `10` and `25`) and the right subtree `40` (right child `50`). Every node is balanced and the root has the height 3. The inorder is still sorted: `10, 20, 25, 30, 40, 50`. The nodes `30` and `40` were not out of balance when the walk up passed them: `30` had a left child only (factor `+1`) and `40` had the children heights 2 and 1 (factor `+1`). Only `20` had a difference of 2.

An ordinary BST with the same keys in this order would be `10 - 20 - 30 - 40 - 50` as a right chain, with `25` hanging left of `30`: height 5 (the chain `10, 20, 30, 40, 50`), against 3 here.
