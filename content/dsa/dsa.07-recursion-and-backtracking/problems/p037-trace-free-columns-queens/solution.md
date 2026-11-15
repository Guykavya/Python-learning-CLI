## Approach

Table method. For each row, list the columns not in `cols`, then cross out those whose `r - c` or `r + c` is taken.

## Expected output

```text
diag [-3, -2, -1]
anti [1, 4, 7]
row 3 free [0, 2]
row 4 free [4]
row 5 free []
stuck
queens [1, 3, 5, 2, 4]
```

## Why

`diag = {-1, -2, -3}` and `anti = {1, 4, 7}`.
Row 3, columns not used: 0, 2, 4. `c = 0`: `3, 3` both free. `c = 2`: `1, 5` both free. `c = 4`: `r - c = -1` is taken. So `[0, 2]`; the program takes the last one, 2, and adds `1` to `diag` and `5` to `anti`.
Row 4, columns left: 0, 4. `c = 0`: `r + c = 4` is taken. `c = 4`: `0` and `8` are free. So `[4]`; it adds `0` and `8`.
Row 5, only column 0 is left: `r + c = 5` is taken (by the queen at row 3, column 2). The row is stuck, and the loop stops after printing `stuck`.
With `free[0]` instead, row 3 gets column 0 and the program completes the solution `[1, 3, 5, 0, 2, 4]`.
