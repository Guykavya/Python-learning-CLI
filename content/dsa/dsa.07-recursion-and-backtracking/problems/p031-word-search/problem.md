# Word search

`board` is a grid of letters, given as a list of rows, each row a list of one-character strings. Write `exist(board, word)` that returns `True` if `word` can be spelled by a path of cells where each step goes to a neighbour **up, down, left or right**, and **no cell is used twice**.

When the function returns, `board` must be exactly as it was (you may change it while searching, but restore every cell).

## Example

```text
A B C E
S F C S
A D E E
```

```python
>>> board = [list("ABCE"), list("SFCS"), list("ADEE")]
>>> exist(board, "ABCCED"), exist(board, "SEE"), exist(board, "ABCB")
(True, True, False)
```

`"ABCB"` fails because the path would have to use the `B` cell twice.

## Constraints

- `1 <= rows, cols <= 6`, `1 <= len(word) <= 15`, letters are upper- and lower-case English letters.

## Think about

How do you remember which cells the current path already uses? The chapter (section 10) overwrites the cell with `"#"` while it is on the path, and puts the letter back afterwards. What happens if you forget to put it back?
