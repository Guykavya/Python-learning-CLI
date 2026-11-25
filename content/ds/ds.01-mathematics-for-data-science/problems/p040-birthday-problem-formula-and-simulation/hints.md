## Hint 1

For the exact formula: multiply the chances that person 2 differs from person 1, person 3 differs from both, and so on. Subtract the product from 1.

## Hint 2

For the simulation: draw an array of shape `(trials, k)` of integers in `0..364`, sort each row, and look for equal neighbours: `(np.diff(sorted_rows, axis=1) == 0).any(axis=1)`.
