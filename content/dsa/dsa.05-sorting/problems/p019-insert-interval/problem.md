# Insert an interval

You have `n` closed intervals that are **already sorted by start** and do **not overlap or touch** each other. Insert one new interval `[a, b]` and merge
everything that overlaps or touches it (touching means sharing an endpoint, so `[1, 2]` and `[2, 5]` merge). Print the resulting sorted list.

## Input

- Line 1: `n`.
- Next `n` lines: `l r`.
- Last line: `a b`.

## Output

One line `l r` per interval of the result.

## Constraints

- `0 <= n <= 200000`
- `0 <= l <= r <= 10^9`, `a <= b`

Because the list is already sorted, an `O(n)` scan is enough; you do not need to sort again.

## Example 1

Input:

```
3
1 2
3 5
6 7
4 6
```

Output:

```
1 2
3 7
```

## Example 2

Input:

```
0
5 7
```

Output:

```
5 7
```
