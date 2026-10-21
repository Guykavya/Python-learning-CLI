# Knight moves

On a chess board, columns (files) are `a` to `h` and rows (ranks) are `1` to `8`. A square
is written like `b1`. A knight moves in an L shape: two squares in one direction and one
square at right angles. In numbers: the file changes by 1 and the rank by 2, or the file by
2 and the rank by 1.

Read a square (capital or small letter, spaces around are fine). Print every square the
knight can move to, on one line separated by spaces, ordered by file (`a` to `h`) and then
by rank (`1` to `8`). Then print `Moves: N`.

If the input is not a valid square, print only `invalid square`.

**Examples**

Input `d4`. Output:
```
b3 b5 c2 c6 e2 e6 f3 f5
Moves: 8
```

Input `A1`. Output:
```
b3 c2
Moves: 2
```
