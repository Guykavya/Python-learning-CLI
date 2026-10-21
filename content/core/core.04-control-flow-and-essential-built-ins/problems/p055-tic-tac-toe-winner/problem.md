# Tic-tac-toe judge

Read a tic-tac-toe board as three lines of three characters each, using `X`, `O` and `.`
(empty). Print exactly one verdict:

- `Invalid board` if: a line does not have exactly 3 characters, a character is not `X`,
  `O` or `.`, the counts are impossible, or the winners are impossible (rules below).
- `X wins` or `O wins` if that player has three in a row (row, column or diagonal).
- `Draw` if the board is full and nobody has won.
- `In progress` otherwise.

X always moves first, and players take turns. So the number of X's is equal to the number of
O's, or one more. If X has won, X must have made the last move, so X's count is O's count + 1.
If O has won, the counts must be equal. Both players winning is impossible.

**Example**

Input:
```
XO.
XO.
X..
```
Output:
```
X wins
```

(Lines are read with `input()` and not stripped; a line `"XO"` is invalid.)
