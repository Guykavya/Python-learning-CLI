## Hint 1

The first `else:` lines up with `for j`, so it belongs to the inner loop. The second `else:` lines up with `for i`,
so it belongs to the outer loop. Which loops contain a `break`?

## Hint 2

`continue` only skips the rest of the current pass (the `count += 1` and `print(i, j)`); the loop then goes on to the
next `j`. It does not stop the loop, so it does not stop the `else` from running.

## Hint 3

For each `i` from 1 to 4, list `j = 1, 2, 3` and print only the pairs where `i + j` is odd. Then print `row i done`.
At `i = 5` the `break` runs before the inner loop. Because the outer loop was broken, its `else` is skipped.
