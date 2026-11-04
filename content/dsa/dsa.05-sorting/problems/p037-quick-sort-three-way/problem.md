# Implement quick sort with three-way partition

Write **quick sort** that stays fast on **every** kind of input. Choose the pivot **at random** (or use median of three), and split the list into three parts:
values `< pivot`, values `== pivot`, values `> pivot`. Recurse only into the first and the last part. Print the sorted list.
`sorted()`, `.sort()`, `heapq` and `bisect` are not allowed: the tests read your source.

The tests include 200000 numbers that are already sorted, reversed, all equal, and drawn from only 3 different values. A quick sort that always uses the first or last element as the pivot, or that puts equal values on one side, needs
`O(n^2)` time (or crashes with `RecursionError`) on those inputs.

## Input

- Line 1: `n`.
- Line 2: `n` integers.

## Output

The sorted list on one line.

## Constraints

- `1 <= n <= 200000`
- `-10^9 <= a[i] <= 10^9`

## Example

Input:

```
9
3 6 1 8 2 9 2 3 3
```

Output:

```
1 2 2 3 3 3 6 8 9
```
