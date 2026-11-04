# Distinct values in every window

For every window of `k` consecutive elements print the number of **distinct** values inside it. Building a set for every
window costs `O(n * k)`. Instead keep **one** frequency dictionary for the current window: when the window slides, add the
new element and remove the old one. A value leaves the dictionary when its count drops to 0, so `len(count)` is always the
number of distinct values.

## Input

- Line 1: `n k`.
- Line 2: `n` integers.

## Output

One line with `n - k + 1` numbers separated by spaces.

## Example

Input:

```
7 4
1 2 1 3 4 2 3
```

Output:

```
3 4 4 3
```

Windows: `1 2 1 3` has 3 distinct, `2 1 3 4` has 4, `1 3 4 2` has 4, `3 4 2 3` has 3.

## Constraints

- `1 <= k <= n <= 200000`
- `-10^9 <= a[i] <= 10^9`
