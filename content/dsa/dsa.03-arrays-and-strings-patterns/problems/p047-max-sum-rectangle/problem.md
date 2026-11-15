# Maximum sum rectangle

Given an `r x c` grid of integers, find the largest sum of a non-empty **rectangle** of cells (a block of consecutive
rows and consecutive columns).

There are about `r^2 c^2 / 4` rectangles: about 130 million for a 150 x 150 grid, too many to try one by one, even with
2D prefix sums. The trick is to fix the **top row** and the **bottom row**. For that band of rows, squash every
column into one number, its sum from top to bottom. A rectangle inside the band is then just a stretch of
consecutive columns, so the best one is a maximum subarray of the squashed row: Kadane.

When the bottom row moves down by one, each column sum grows by one cell, so the squashed row is updated in O(c),
not rebuilt.

## Input

- Line 1: `r` and `c`.
- Then `r` lines with `c` integers each.

## Output

One line: the largest rectangle sum.

## Example

Input:

```
4 5
1 2 -1 -4 -20
-8 -3 4 2 1
3 8 10 1 3
-4 -1 1 7 -6
```

Output:

```
29
```

The best rectangle is rows 2 to 4, columns 2 to 4:

```
-3  4  2
 8 10  1
-1  1  7
```

Its sum is `3 + 19 + 7 = 29`.

## Constraints

- `1 <= r, c <= 150`
- `-10^6 <= value <= 10^6`
- The rectangle must contain at least one cell, so if every value is negative the answer is the largest single value.

Use `input()` without a prompt message.
