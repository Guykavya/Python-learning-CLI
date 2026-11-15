# Trace: is this queen placement safe?

On a 6x6 board, queens are already placed in rows 0, 1, 2 at columns 1, 3, 5. The program computes the diagonal sets, then keeps adding a queen to the next row in the **last** free column, printing the free columns of each row, until the board is full or a row has no free column.

Predict **exactly** what it prints. Do not run it.

```python
n = 6
queens = [1, 3, 5]          # queens[r] = column of the queen in row r
cols = set(queens)
diag = {r - c for r, c in enumerate(queens)}
anti = {r + c for r, c in enumerate(queens)}
print("diag", sorted(diag))
print("anti", sorted(anti))

r = len(queens)
while r < n:
    free = [c for c in range(n)
            if c not in cols and r - c not in diag and r + c not in anti]
    print("row", r, "free", free)
    if not free:
        print("stuck")
        break
    c = free[-1]
    queens.append(c)
    cols.add(c)
    diag.add(r - c)
    anti.add(r + c)
    r += 1
print("queens", queens)
```

Write your answer in `answer.txt`, one printed line per line, exactly as Python prints it (for example `row 3 free [0, 2]`).

## How to work

For row `r`, column `c` is free only if `c` is not in `cols`, `r - c` is not in `diag`, and `r + c` is not in `anti`. Make a small table for each row: `c`, `r - c`, `r + c`, and mark which test fails. Remember to update the three sets after each placement.

## After you answer

1. Draw the final board. Which queen blocks the last free square of the stuck row?
2. Change `free[-1]` to `free[0]`. Does the program reach row 5? (`[1, 3, 5, 0, 2, 4]` is a solution.)
