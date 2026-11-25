## Hint 1

Look down each column of the ridge table, then of the lasso table. Which one has exact zeros?

## Hint 2

The ridge penalty `alpha * b^2` has a derivative that goes to 0 at b = 0. The lasso penalty `alpha * |b|` has a corner at 0, and its 'pull' stays at the same strength however small b is.
