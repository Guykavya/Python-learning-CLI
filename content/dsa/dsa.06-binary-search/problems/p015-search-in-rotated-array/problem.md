# Search in a rotated sorted array

A list of **distinct** integers was sorted in increasing order and then rotated (for example `[6, 7, 9, 15, 19, 2, 3, 4]`; a rotation by 0 is allowed). For every query print the index of the target, or `-1`.

The trick: at every step at least one half, `lo..mid` or `mid..hi`, is sorted. Find which one, and ask whether the target lies inside it.
`bisect`, `index`, `count` and `in` are not allowed.

## Input

- Line 1: `n`. Line 2: the `n` rotated numbers.
- Line 3: `q`. Line 4: `q` targets.

## Output

`q` lines: the index of each target, or `-1`.

## Constraints

- `1 <= n <= 100000`, `1 <= q <= 100000`, values distinct, `-10^9 <= a[i], x <= 10^9`

## Example

Input:

```
8
6 7 9 15 19 2 3 4
4
3 19 8 6
```

Output:

```
6
4
-1
0
```
