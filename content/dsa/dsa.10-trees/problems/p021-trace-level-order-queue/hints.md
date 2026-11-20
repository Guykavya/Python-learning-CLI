## Hint 1

The queue starts as `[8]`. `level 1: size 1`. Pop `8`: its children `3` and `10` go to the back, so the queue after the pop is `[3, 10]`. That is the first `pop` line. Then the inner loop is over, the level `[8]` is stored, and the outer loop starts level 2 with the queue `[3, 10]`.

## Hint 2

Level 2 has size 2. Pop `3`: it adds `1` and `6`, so the queue is `[10, 1, 6]`. Pop `10`: it has no left child and the right child `14`, so the queue is `[1, 6, 14]`. Level 3 starts with `size 3`. Its three nodes are leaves, so the queue only shrinks: `[6, 14]`, `[14]`, `[]`.
