# Trace an in-place rotation, layer by layer

This function rotates a square grid 90 degrees **clockwise** without a second grid. It works on rings ("layers"),
from the outside in. In each step it moves four cells at once: left to top, bottom to left, right to bottom, and
the saved top to right. After each 4-way move it prints the four positions `(row,col)` with their **new** values,
in the order top, right, bottom, left. Predict **exactly** what the program prints. Do not run it.

```python
def rotate(m):
    n = len(m)
    for layer in range(n // 2):
        first = layer
        last = n - 1 - layer
        for i in range(first, last):
            offset = i - first
            top = m[first][i]                                  # save the top cell
            m[first][i] = m[last - offset][first]              # left   -> top
            m[last - offset][first] = m[last][last - offset]   # bottom -> left
            m[last][last - offset] = m[i][last]                # right  -> bottom
            m[i][last] = top                                   # top    -> right
            print(f"layer {layer} i {i}:",
                  f"({first},{i})={m[first][i]}",
                  f"({i},{last})={m[i][last]}",
                  f"({last},{last - offset})={m[last][last - offset]}",
                  f"({last - offset},{first})={m[last - offset][first]}")


m = [[1, 2, 3, 4],
     [5, 6, 7, 8],
     [9, 10, 11, 12],
     [13, 14, 15, 16]]
rotate(m)
for row in m:
    print(*row)
```

Write your answer in `answer.txt`, one line per printed line. A move line looks like
`layer 0 i 0: (0,0)=13 (0,3)=1 (3,3)=4 (3,0)=16` (that is the first line).

## How to work

1. For every step write down `layer`, `first`, `last`, `i` and `offset`. Then compute the four positions:
   top `(first, i)`, right `(i, last)`, bottom `(last, last - offset)`, left `(last - offset, first)`.
2. Read the **old** values at those four positions from your current grid. The new values are: top gets the old
   left, right gets the old top, bottom gets the old right, left gets the old bottom.
3. Update your copy of the grid before the next step. (Here no step touches a cell that an earlier step changed,
   but check that yourself.)

How many steps does the outer layer of a 4 x 4 grid need, and how many does the inner 2 x 2 layer need?

## After you answer

1. Every cell `(r, c)` should end at `(c, n - 1 - r)`. Check it for the value 2 (start `(0,1)`) and 12 (start `(2,3)`).
2. Why does the inner loop run `i` from `first` to `last - 1`, and not up to `last`? What would the extra step do?
3. How many 4-way moves does an `n x n` rotation need in total? (Each move places 4 cells.)
