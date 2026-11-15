# Search a 2D matrix

A matrix with `R` rows and `C` columns has these properties: every row is sorted ascending, and the first number of each row is **larger than the last number of the previous row**. All numbers are distinct.
So if you read the matrix row by row, you get one long sorted list of `R * C` numbers.

For each query print the position `row col` (0-based) of the number, or `-1 -1`.

Do **not** flatten the matrix into a new list for every query. Binary search on the virtual index `i` in `[0, R*C - 1]` and translate it with `row = i // C`, `col = i % C`.
`bisect`, `index`, `count` and `in` are not allowed.

## Input

- Line 1: `R C`. Then `R` lines of `C` integers.
- Next line: `q`. Then one line with `q` integers.

## Output

`q` lines of the form `row col` or `-1 -1`.

## Constraints

- `1 <= R, C <= 1000`, `R * C <= 500000`, `1 <= q <= 100000`
- values and queries between `-10^9` and `10^9`

## Example

Input:

```
3 4
1 3 5 7
10 11 16 20
23 30 34 60
4
3 13 60 1
```

Output:

```
0 1
-1 -1
2 3
0 0
```
