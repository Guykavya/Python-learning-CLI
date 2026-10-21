## Hint 1

In `down_up`, the first print happens before the recursive call, the second after it returns.

## Hint 2

Draw the calls as a tree for `tree(2)`: it calls `tree(1)` twice, and each of those calls `tree(0)` twice.

## Hint 3

`build(3)` returns a value built on the way back up. Work from the base case upwards.
