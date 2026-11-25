## Hint 1

Compute the test block size first: `12 // (3 + 1)`. The three test blocks are the last three blocks of that size.

## Hint 2

For each fold the training rows run from 0 to just before the test block; with `gap = 1` the last training row moves one step earlier.
