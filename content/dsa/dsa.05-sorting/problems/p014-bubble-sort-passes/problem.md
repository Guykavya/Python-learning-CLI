# Bubble sort with early exit

Implement **bubble sort** by hand. One *pass* compares every adjacent pair `(a[0], a[1])`, `(a[1], a[2])`, ... and swaps the pair when the left value is strictly larger.
Keep making passes until a pass makes **no swap**; that last pass is also counted. Print the number of passes, the total number of swaps, and the sorted list.
`sorted()`, `.sort()`, `heapq` and `bisect` are not allowed: the tests read your source.

## Input

- Line 1: `n`.
- Line 2: `n` integers.

## Output

- Line 1: number of passes (including the final pass without swaps).
- Line 2: total swaps.
- Line 3: the sorted list.

## Constraints

- `1 <= n <= 2000`

An already sorted list needs exactly 1 pass and 0 swaps.

## Example 1

Input:

```
5
5 1 4 2 8
```

Output:

```
3
4
1 2 4 5 8
```

## Example 2

Input:

```
3
1 2 3
```

Output:

```
1
0
1 2 3
```
