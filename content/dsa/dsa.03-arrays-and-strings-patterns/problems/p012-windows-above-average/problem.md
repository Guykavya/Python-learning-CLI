# Count windows with a high average

A sensor gives `n` integer readings. Count the windows of exactly `k` neighbouring readings whose **average** is at
least `t`.

The average of a window is `sum / k`. Comparing `sum / k >= t` uses floats; compare `sum >= t * k` instead. It means
the same thing (because `k > 0`) and stays in exact integers. Slide the window so that each step costs O(1).

## Input

- Line 1: `n k t`.
- Line 2: `n` integers.

## Output

The number of windows of size `k` with average `>= t`.

## Example

Input:

```
7 3 4
1 3 5 2 6 4 0
```

Output:

```
2
```

The threshold is `t * k = 12`. The five window sums are `9, 10, 13, 12, 10`. Two reach 12: `5 2 6 = 13` and
`2 6 4 = 12` (average exactly 4 counts, because the rule is "at least").

## Constraints

- `1 <= k <= n <= 200000`
- `-10^4 <= a[i], t <= 10^4`
