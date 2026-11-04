# Minimum meeting rooms

Meetings are half-open intervals `[start, end)`: a meeting that ends at 5 frees its room for one that starts at 5. Print the **minimum number of rooms**
needed so that no two meetings share a room at the same time. That number equals the largest number of meetings running at the same moment.

## Input

- Line 1: `n`.
- Next `n` lines: `start end` with `start < end`.

## Output

One integer.

## Constraints

- `0 <= n <= 200000`
- `0 <= start < end <= 10^9`

Hint on method: you do not need to match meetings to rooms. Sort the **start times** and the **end times** separately, and sweep with two pointers.

## Example 1

Input:

```
3
0 30
5 10
15 20
```

Output:

```
2
```

## Example 2

Input:

```
3
7 10
2 4
4 7
```

Output:

```
1
```
