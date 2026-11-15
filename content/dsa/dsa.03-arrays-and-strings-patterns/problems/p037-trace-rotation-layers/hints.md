## Hint 1

Layer 0 has `first = 0`, `last = 3`, and `i` runs over 0, 1, 2 (three moves). Layer 1 has `first = 1`, `last = 2`,
and `i` runs over just 1 (one move). So there are 4 move lines, then 4 grid rows.

## Hint 2

For layer 0, `i = 1`: `offset = 1`. The four positions are top `(0,1)`, right `(1,3)`, bottom `(3,2)`, left `(2,0)`,
holding 2, 8, 15, 9 before the move. Top gets the old left (9), right gets the old top (2), bottom gets the old
right (8), left gets the old bottom (15).

## Hint 3

The final grid is the clockwise rotation: the first row of the result is the first column of the original, read
from the bottom up: `13 9 5 1`.
