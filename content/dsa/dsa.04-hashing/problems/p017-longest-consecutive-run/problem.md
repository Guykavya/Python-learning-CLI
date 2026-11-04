# Longest run of consecutive values

Given `n` integers in any order (possibly with repeats), find the length of the longest group of values that are
consecutive integers, such as `4, 5, 6, 7`. The values do not need to be next to each other in the input.

Sorting works in O(n log n). Try the O(n) idea: put all values in a set, and only start counting at a value `x` for
which `x - 1` is **not** in the set (the start of a run).

## Input

- Line 1: `n`.
- Line 2: `n` integers (an empty line when `n = 0`).

## Output

One integer: the longest run length (`0` when `n = 0`).

## Example

Input:

```
6
100 4 200 1 3 2
```

Output:

```
4
```

`1, 2, 3, 4` is a run of length 4. `100` and `200` are runs of length 1. With repeats `1 1 2` the answer is `2`.

## Constraints

- `0 <= n <= 200000`
- `-10^9 <= a[i] <= 10^9`
