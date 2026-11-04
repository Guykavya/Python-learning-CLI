# Floor and ceiling

A sorted list (duplicates allowed) and queries. For each query `x` print two things on one line:

- the **floor**: the largest element `<= x`
- the **ceiling**: the smallest element `>= x`

If there is no such element print `none` in its place. If `x` is in the list, floor and ceiling are both `x`.
Write the search yourself: `bisect`, `index`, `count` and `in` are not allowed.

## Input

- Line 1: `n`. Line 2: `n` integers in non-decreasing order.
- Line 3: `q`. Line 4: `q` integers.

## Output

`q` lines of the form `floor ceiling`.

## Constraints

- `1 <= n <= 100000`, `1 <= q <= 100000`
- `-10^9 <= a[i], x <= 10^9`

## Example

Input:

```
5
10 20 20 30 50
5
20 25 5 60 50
```

Output:

```
20 20
20 30
none 10
50 none
50 50
```
