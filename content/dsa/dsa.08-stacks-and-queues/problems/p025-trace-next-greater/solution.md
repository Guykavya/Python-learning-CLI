## Approach

Keep `waiting` as a list of indices and `ans` as a list of five numbers. For each new `x`, pop every waiting index whose value is strictly smaller than `x` and write `x` into its answer; then push the new index.

## Expected output

```text
0 2 [0] [-1, -1, -1, -1, -1]
1 1 [0, 1] [-1, -1, -1, -1, -1]
pop 1
2 2 [0, 2] [-1, 2, -1, -1, -1]
pop 2
pop 0
3 4 [3] [4, 2, 4, -1, -1]
4 3 [3, 4] [4, 2, 4, -1, -1]
[4, 2, 4, -1, -1]
```

## Why

- `i = 2`: index 1 (value 1) is resolved by 2. Index 0 has value 2, and `2 < 2` is false, so it keeps waiting: the next greater element must be **strictly** greater.
- `i = 3`: 4 resolves index 2 (value 2), then index 0 (value 2). The pops come out top first: `pop 2` before `pop 0`.
- Indices 3 and 4 (values 4 and 3) never meet anything greater, so they keep `-1`.

The values in `waiting` were `[2]`, `[2, 1]`, `[2, 2]`, `[4]`, `[4, 3]`: never increasing from bottom to top. Five pushes and three pops: every index is pushed once and popped at most once, so the whole scan is `O(n)`.
