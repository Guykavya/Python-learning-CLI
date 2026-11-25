## Approach

Both rules look at the same difference `mean - median` but divide it by different things: `skew_hint` by the spread (a scale for *this* data), `compare_centres` by the size of the median (a percentage of the level). A tight cluster far from zero (100 to 110) is clearly lopsided relative to its own spread, yet 1.2 on a level of 102 is only about 1%. The exact printed lines are in `expected.txt`, from a real run.

## Code

See the program in the problem statement.

## Complexity

Each dataset has 5 values: O(n) per call.

## Another way

`skew_hint` is Pearson's second skewness coefficient divided by 3; the better number is the skewness of section 14.5.
