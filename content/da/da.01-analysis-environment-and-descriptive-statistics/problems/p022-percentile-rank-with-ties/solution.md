## Approach

Four small counts. 60: below 1, equal 2 gives 25.0. 70: below 3, equal 3 gives 56.25, printed with one decimal. 55: below 1, equal 0 gives 12.5. 90: below 7, equal 1 gives 93.75, printed with one decimal. The exact lines are in `expected.txt` from a real run (note the two halfway roundings).

## Code

See the program in the problem statement.

## Complexity

O(n) per score.

## Another way

Sort once and use `bisect_left` and `bisect_right`: `below = bisect_left(s, score)`, `equal = bisect_right(s, score) - below`. That is O(log n) per score after an O(n log n) sort.
