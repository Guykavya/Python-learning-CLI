## Hint 1

Think about what one shift does to the number of inversions. Does it remove one, or more?

## Hint 2

Each shift moves a larger value past `key`, fixing exactly one inversion. So shifts = inversions, and the outer loop adds `n - 1` more steps.

## Hint 3

For tiny pieces (about 16 to 64 items) the simple loop has no recursion overhead and runs on data that is cache friendly, so it beats the clever sorts.
