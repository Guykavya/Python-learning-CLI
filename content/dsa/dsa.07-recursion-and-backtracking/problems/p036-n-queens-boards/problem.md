# N-Queens boards

Write `solve_n_queens(n)` that returns **all** solutions of the N-Queens puzzle. Each solution is a board: a list of `n` strings of length `n`, with `"Q"` for a queen and `"."` for an empty square. The order of the solutions does not matter.

## Example

```python
>>> for board in solve_n_queens(4):
...     print(board)
['.Q..', '...Q', 'Q...', '..Q.']
['..Q.', 'Q...', '...Q', '.Q..']
>>> solve_n_queens(1)
[['Q']]
>>> solve_n_queens(3)
[]
```

## Constraints

- `1 <= n <= 8`.

## Think about

Store each solution as the list `cols_of` (the column of the queen in each row) while searching, and turn it into strings only at the end. What does the row string look like when the queen is in column `c`?
