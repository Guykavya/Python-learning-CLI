# Largest sum of a window of size k

A **window** of size `k` is a run of `k` neighbouring elements. Find the largest sum of any window of size `k`.

Re-adding all `k` elements for each window costs `n * k` steps. Instead **slide** the window: when it moves one step
right, one element enters on the right and one leaves on the left, so

```
new sum = old sum + entering element - leaving element
```

## Input

- Line 1: `n k`.
- Line 2: `n` integers.

## Output

The largest window sum.

## Example

Input:

```
7 3
2 -1 4 1 -6 5 3
```

Output:

```
5
```

The window sums are `5, 4, -1, 0, 2`. The first window `2 -1 4` is the best. (The last window `-6 5 3` sums to 2.)

## Constraints

- `1 <= k <= n <= 200000`
- `-10^9 <= a[i] <= 10^9` (all values may be negative)
