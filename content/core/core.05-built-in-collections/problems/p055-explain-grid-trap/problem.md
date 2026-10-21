# Explain the [[0] * 3] * 3 bug

A student writes:

```python
board = [[0] * 3] * 3
board[1][1] = 5
print(board)
```

and gets `[[0, 5, 0], [0, 5, 0], [0, 5, 0]]` instead of a single 5 in the middle.

Explain in your own words, in `answer.md`:

1. What `[0] * 3` builds, and why sharing the `0` objects causes no problem.
2. What the outer `* 3` builds. Draw a memory diagram.
3. Why `board[1][1] = 5` changes "every row".
4. How to prove the rows are the same object, using `is`.
5. Two correct ways to build the board, and why they work.
6. Another expression with the same trap that does not involve numbers.
