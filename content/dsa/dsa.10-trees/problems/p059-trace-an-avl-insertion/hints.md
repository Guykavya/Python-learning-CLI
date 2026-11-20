## Hint 1

`10`, then `20` goes to the right of `10`: no rotation (the balance factor of `10` is `-1`). `30` goes under `20`: now `10` has the balance factor `-2` and its right child `20` is not left-heavy, so one left rotation at `10` makes `20` the top with the children `10` and `30`: that is one `rotate_left at 10` line, printed before `insert 30: [20, 10, 30]`. `40` goes right of `30`: all factors are within `-1..1`, so no rotation.

## Hint 2

`50` goes right of `40`: the node `30` has the factor `-2` (no left child, right height 2). Its right child `40` is right-heavy, so a single left rotation at `30`: `40` becomes the parent of `30` and `50`, under `20`. Then `25`: it goes `20 -> 40 -> 30 -> left of 30`. On the way up `30` and `40` are fine, but `20` has the factor `-2` (left height 1, right height 3) and its right child `40` is **left-heavy** (factor `+1`). That is the right-left case: first `rotate_right at 40` (this makes `30` the new right child of `20`), then `rotate_left at 20`.
