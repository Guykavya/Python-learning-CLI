## Hint 1

The tree is `5` with left child `2` and right child `7`; `2` has children `1` and `4`; `7` has the left child `6`. Start with `cur = 5`, the stack empty. The inner loop pushes `5`, then `2`, then `1`, and stops when `cur` becomes the left child of `1`, which is `None`. That already gives three `push` lines.

## Hint 2

Then `pop 1` (stack is now `[5, 2]`, `out=[1]`), and `cur` becomes the right child of `1`, which is `None`, so the inner loop does nothing and the next line is `pop 2`. After `pop 2`, `cur` is `4`: you get a `push 4`. Continue the same way; the lines for the right side of the tree are `push 7`, `push 6`, `pop 6`, `pop 7`.
