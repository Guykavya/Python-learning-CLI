## Hint 1

Row 0 has no row above it, so every cell there is "0 + the cell to the left". The start cell is set to 1 by the `elif`. What does that give for the whole first row?

## Hint 2

Row 1: column 0 has no left neighbour, so it copies the cell above (1). Column 1 is `1 + 1 = 2`. Column 2 is the obstacle: 0. Column 3 is "above + left" = `1 + 0`, because its left neighbour is the obstacle.

## Hint 3

Keep going with the same rule. In row 3, column 0 is an obstacle (0), so column 1 gets only the paths from above: `f[2][1] + 0`. The last cell is `f[2][3] + f[3][2]`.
