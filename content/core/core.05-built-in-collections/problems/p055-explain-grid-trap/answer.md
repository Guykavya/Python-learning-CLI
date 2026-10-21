**1. The inner part.** `[0] * 3` builds one new list with three references to the int object
`0`. Sharing is harmless because an int can never change. `row[1] = 5` does not modify the
`0`; it **replaces** the reference in slot 1 with a reference to `5`.

**2. The outer part.** `[row] * 3` builds a list with three references to **the same row
object**. It does not copy the row.

```
board --> [ o , o , o ]
            |   |   |
            +---+---+
                |
                v
            [ o , o , o ]   the only row
              |   |   |
              +---+---+--> 0
```

**3. Why every row changes.** `board[1]` is the shared row. `board[1][1] = 5` replaces slot 1
of that row. `board[0]` and `board[2]` are the same row, so printing shows 5 three times. Only
one change was made; it is seen three times.

**4. Proof.** `print(board[0] is board[1], board[1] is board[2])` prints `True True`.

**5. Correct ways.**

```python
board = [[0] * 3 for _ in range(3)]
```

The comprehension evaluates `[0] * 3` once per row, so it makes three separate lists.

```python
board = []
for _ in range(3):
    board.append([0] * 3)
```

Same idea: a new row each time round the loop.

**6. Same trap elsewhere.** `buckets = [[]] * 3` then `buckets[0].append("x")` gives
`[['x'], ['x'], ['x']]`. `[{}] * 3` has the same problem with dicts. The rule: `[x] * n` is
safe only when `x` is immutable.

Key ideas to check: `*` repeats references; immutable ints make the inner repeat harmless;
the outer repeat shares one mutable row; diagram; `is` proof; comprehension fix.
