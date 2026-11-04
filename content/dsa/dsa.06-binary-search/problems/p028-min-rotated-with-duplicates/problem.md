# Minimum in a rotated array with duplicates

Now the rotated sorted array may contain **equal values**, for example `[3, 3, 1, 3]` or `[1, 1, 0, 1, 1]`. Find the minimum.
The rule "compare `a[mid]` with `a[hi]`" has one extra case: when `a[mid] == a[hi]` you cannot tell on which side the drop is (`[3, 3, 1, 3]` and `[3, 1, 3, 3]` both have `a[mid] == a[hi]`). What is the safe thing to do?
Because of this case the worst case is `O(n)`, for example `[1, 1, 1, 1, 0, 1, 1]`.

Several test cases in one input. `min`, `max`, `sorted`, `.sort` are not allowed.

## Input

- Line 1: `t`, the number of test cases.
- For each case: a line with `n`, then a line with `n` integers.

## Output

`t` lines: the minimum of each array.

## Constraints

- `1 <= t <= 2000`, `1 <= n <= 100000`, total size at most `300000`
- `-10^9 <= a[i] <= 10^9`

## Example

Input:

```
3
4
3 3 1 3
5
1 1 0 1 1
3
2 2 2
```

Output:

```
1
0
2
```
