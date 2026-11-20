## Approach

Keep `cur`, the stack and `out` in a table and follow the two loops exactly: the inner loop pushes while it can go left; then one pop, one visit, and a move to the right child.

## Expected output

```text
push 5: stack=[5]
push 2: stack=[5, 2]
push 1: stack=[5, 2, 1]
pop 1: stack=[5, 2] out=[1]
pop 2: stack=[5] out=[1, 2]
push 4: stack=[5, 4]
pop 4: stack=[5] out=[1, 2, 4]
pop 5: stack=[] out=[1, 2, 4, 5]
push 7: stack=[7]
push 6: stack=[7, 6]
pop 6: stack=[7] out=[1, 2, 4, 5, 6]
pop 7: stack=[] out=[1, 2, 4, 5, 6, 7]
[1, 2, 4, 5, 6, 7]
```

## Why

| step | action | `cur` afterwards | stack after |
|---|---|---|---|
| 1-3 | push 5, 2, 1 going left | `None` (left of 1) | `[5, 2, 1]` |
| 4 | pop 1, visit | `None` (right of 1) | `[5, 2]` |
| 5 | pop 2, visit | `4` (right of 2) | `[5]` |
| 6 | push 4 (it has no left child) | `None` | `[5, 4]` |
| 7 | pop 4, visit | `None` | `[5]` |
| 8 | pop 5, visit | `7` (right of 5) | `[]` |
| 9-10 | push 7, then 6 going left | `None` | `[7, 6]` |
| 11 | pop 6, visit | `None` | `[7]` |
| 12 | pop 7, visit | `None` | `[]` |

At every moment the stack holds the **ancestors that are waiting**: nodes whose left subtree is being processed, so their own turn has not come. The visit order `1, 2, 4, 5, 6, 7` is the inorder. The stack is never larger than 3, which is the height of the tree (`5 - 2 - 1`). The outer condition is `cur or stack` because after the very last pop `cur` is `None` while the stack may still hold nodes, and at the start `cur` is set but the stack is empty.
