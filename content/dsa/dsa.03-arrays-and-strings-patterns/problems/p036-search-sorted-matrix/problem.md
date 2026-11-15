# Staircase search in a sorted grid

Every row of the grid is sorted from left to right, and every column is sorted from top to bottom (equal values
are allowed). For each query value, print `yes` if it appears in the grid and `no` otherwise.

Use the sorted order: start at the **top-right corner**. From there, one comparison always rules out a whole row
or a whole column, so a search takes at most `r + c` steps.

## Input

- Line 1: `r c`.
- Next `r` lines: `c` integers each (rows and columns sorted, non-decreasing).
- Next line: `q`.
- Next line: `q` query values.

## Output

`q` lines, `yes` or `no`, one per query in order.

## Example

Input:

```
3 4
1 4 7 11
2 5 8 12
3 6 9 16
3
5 10 16
```

Output:

```
yes
no
yes
```

Searching 5: `11` is too big (move left), `7` is too big (left), `4` is too small (down), `5` found.
Searching 10: `11` (left), `7` (down), `8` (down), `9` (down), and the walk leaves the grid at the bottom: `no`.

## Constraints

- `1 <= r, c <= 600`
- `1 <= q <= 2000`
- `-10^9 <= values <= 10^9`

Use `input()` without a prompt message.
