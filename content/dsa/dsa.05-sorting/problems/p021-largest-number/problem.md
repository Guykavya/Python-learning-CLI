# Largest number from digits

Given `n` non-negative integers, arrange them in an order so that the **concatenation** of their decimal strings is the largest possible number.
Print that number as a string (it can be huge). If every number is `0`, print `0` (not `000`).

## Input

- Line 1: `n`.
- Line 2: `n` non-negative integers.

## Output

The largest concatenation.

## Constraints

- `1 <= n <= 100000`
- `0 <= a[i] <= 10^9`

Sorting numbers numerically or sorting the strings alphabetically does not work: `9` must come before `34`, and `3` before `30`.
The right rule compares **pairs**: `x` goes before `y` when `x + y > y + x` as strings.

## Example 1

Input:

```
5
3 30 34 5 9
```

Output:

```
9534330
```

## Example 2

Input:

```
3
0 0 0
```

Output:

```
0
```
