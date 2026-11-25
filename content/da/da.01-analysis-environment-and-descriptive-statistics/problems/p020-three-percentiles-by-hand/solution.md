## Approach

Positions first, values second. p=25: nearest-rank rank 2, so 20; inclusive position 1.0, so 20 exactly; exclusive position 1.5, so halfway between 15 and 20, 17.5. p=50: all three give 35. p=90: nearest-rank 50, inclusive 46 (40 plus 0.6 times 10), exclusive error. The printed lines are in `expected.txt` from a real run (compare with the library numbers in the statement for p=25 and p=50).

## Code

See the program in the problem statement.

## Complexity

O(n log n) per call (sorting).

## Another way

`statistics.quantiles(data, n=100, method=...)` returns 99 cut points at once; it clamps instead of raising, so at `p=90` on five values its exclusive answer is 50, the maximum.
