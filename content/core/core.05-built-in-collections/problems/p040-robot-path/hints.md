## Hint 1

Store each cell as a tuple `(x, y)`. Why a tuple and not a list?

## Hint 2

Keep `visited = {(0, 0)}`. After each move, if the new cell is in `visited`, count a revisit;
then add it.

## Hint 3

A dict maps each letter to its step: `{"U": (0, 1), "D": (0, -1), "L": (-1, 0), "R": (1, 0)}`.
