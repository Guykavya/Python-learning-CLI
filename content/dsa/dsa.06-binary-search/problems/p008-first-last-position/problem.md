# First and last position

For each query `x` print the index of its **first** and **last** occurrence in a sorted list (duplicates allowed), separated by a space. If `x` is not in the list print `-1 -1`.

Tie rule: first = smallest index with value `x`, last = largest index with value `x`. A value that appears once has `first == last`.
`bisect`, `index`, `count` and `in` are not allowed.

## Input

- Line 1: `n`. Line 2: `n` integers in non-decreasing order.
- Line 3: `q`. Line 4: `q` integers.

## Output

`q` lines of the form `first last`, or `-1 -1`.

## Constraints

- `1 <= n <= 100000`, `1 <= q <= 100000`
- `-10^9 <= a[i], x <= 10^9`

## Example

Input:

```
8
1 2 2 2 5 7 7 9
4
2 7 3 9
```

Output:

```
1 3
5 6
-1 -1
7 7
```
