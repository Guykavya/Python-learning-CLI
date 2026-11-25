## Approach

For every `(i, j)` multiply row `i` of `A` by column `j` of `B` entry by entry and add. `C` has 2 rows and 3 columns, so six lines.

## Answer

```text
C[0][0] = 5 + 16 = 21
C[0][1] = 6 + 18 = 24
C[0][2] = 7 + 20 = 27
C[1][0] = 15 + 32 = 47
C[1][1] = 18 + 36 = 54
C[1][2] = 21 + 40 = 61
```

## Another way

Check with NumPy: `np.array(A) @ np.array(B)` gives `[[21, 24, 27], [47, 54, 61]]`.
