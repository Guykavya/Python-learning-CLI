# Maximum subarray sum (Kadane)

A **subarray** is a run of neighbouring elements, with at least one element. Find the largest possible sum of a
subarray.

Kadane's idea: walk once from left to right and keep `cur`, the best sum of a subarray that **ends at the current
element**. For the next element `x` there are only two choices: extend the old run (`cur + x`) or start fresh at `x`.

```
cur = max(x, cur + x)
best = max(best, cur)
```

## Input

- Line 1: `n`.
- Line 2: `n` integers.

## Output

The largest subarray sum.

## Example

Input:

```
9
-2 1 -3 4 -1 2 1 -5 4
```

Output:

```
6
```

The subarray `4 -1 2 1` sums to 6. No other run does better.

If every element is negative, the answer is the largest (least negative) element: a subarray must contain at least
one element, so the answer is never 0 for such an input.

## Constraints

- `1 <= n <= 200000`
- `-10^9 <= a[i] <= 10^9`
