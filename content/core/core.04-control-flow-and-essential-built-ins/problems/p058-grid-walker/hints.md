## Hint 1

Keep three pieces of state: `x`, `y` and `facing` (a string like `"north"`). Each command
changes some of them.

## Hint 2

Turning right from north gives east, then south, then west, then north again. A `match` on
`facing` can give the new direction. Turning left is the opposite; turning around is two rights.

## Hint 3

For `move N`: loop N times; work out the next square with a `match` on `facing` (north adds 1
to `y`, and so on); if it is outside `0 <= nx < W` and `0 <= ny < H`, print the bump message
and `break`; otherwise move and count the step.
