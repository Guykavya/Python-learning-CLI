# Classic binary search

You get a sorted list of **distinct** integers and several queries. For every query print the 0-based index of that number in the list, or `-1` if it is not there.

Write the search yourself. `bisect`, `list.index`, `list.count` and the `in` operator are not allowed in this problem: the point is to write the loop.

Use the closed template from the chapter: `lo = 0`, `hi = n - 1`, `while lo <= hi`, `mid = (lo + hi) // 2`.
Think about the invariant: *if the target is in the list, it lies inside `a[lo..hi]`*.

## Input

- Line 1: `n`.
- Line 2: `n` integers in strictly increasing order.
- Line 3: `q`, the number of queries.
- Line 4: `q` integers (the targets).

## Output

`q` lines: the index of each target, or `-1`.

## Constraints

- `1 <= n <= 100000`, `1 <= q <= 100000`
- `-10^9 <= a[i], target <= 10^9`

## Example

Input:

```
5
2 5 8 12 16
4
8 2 16 9
```

Output:

```
2
0
4
-1
```
