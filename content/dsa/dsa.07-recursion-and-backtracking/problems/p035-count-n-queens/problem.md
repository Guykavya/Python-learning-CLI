# Count N-Queens solutions

Place `n` queens on an `n x n` chessboard so that no two attack each other (no two in the same row, column or diagonal). Write `total_n_queens(n)` that returns the **number** of different placements.

Use one queen per row and keep three sets, as in chapter section 11: the used columns, the used diagonals (`r - c`) and the used anti-diagonals (`r + c`). Each safety check is then three set look-ups.

## Example

```python
>>> [total_n_queens(n) for n in range(1, 9)]
[1, 0, 0, 2, 10, 4, 40, 92]
```

## Constraints

- `1 <= n <= 9`. `n = 9` has 352 solutions and must finish in a few seconds.

## Think about

You do not need to store the boards, only count them. What does the call for row `r == n` return?
