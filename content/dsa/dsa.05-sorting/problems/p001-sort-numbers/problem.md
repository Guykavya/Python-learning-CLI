# Sort numbers up and down

Read `n` integers. Print them sorted from smallest to largest on the first line, and sorted from largest to smallest on the second line.
Separate numbers with one space. Python's built-in sorting is exactly what you should use here.

## Input

- Line 1: `n`.
- Line 2: `n` integers (an empty line when `n = 0`).

## Output

Two lines: ascending, then descending. For `n = 0` print two empty lines (or nothing: both are accepted).

## Constraints

- `0 <= n <= 200000`
- `-10^9 <= a[i] <= 10^9`

## Example

Input:

```
6
3 -1 4 1 -5 9
```

Output:

```
-5 -1 1 3 4 9
9 4 3 1 -1 -5
```
