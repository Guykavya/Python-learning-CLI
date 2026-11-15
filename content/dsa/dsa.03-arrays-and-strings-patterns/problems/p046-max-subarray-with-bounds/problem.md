# Maximum subarray with its bounds

Kadane's algorithm finds the largest sum of a non-empty contiguous subarray. Here you must also say **where** that
subarray is: print the sum and its 1-based bounds `l r`.

Several subarrays can share the maximum sum, so the answer is pinned by a **tie rule**:

1. among all subarrays with the maximum sum, choose the one with the **smallest `l`** (earliest start);
2. if several of those start at the same `l`, choose the **shortest** one (smallest `r`).

Getting the rule right is the real point of this problem: Kadane has two comparisons (when to restart the current
run, and when to replace the best), and each one decides one half of the rule.

## Input

- Line 1: `n`.
- Line 2: `n` integers (they can be negative or zero).

## Output

One line: `sum l r`.

## Example

Input:

```
8
-2 1 -3 4 -1 2 1 -5
```

Output:

```
6 4 7
```

The subarray `4 -1 2 1` (positions 4 to 7) has sum 6.

More tie examples:

| input | output | why |
|---|---|---|
| `-1 0 2` | `2 2 3` | `0 2` (from 2) and `2` (from 3) both sum to 2; the earlier start wins |
| `2 -2 2` | `2 1 1` | `2`, `2 -2 2` and the last `2` all sum to 2; start 1 wins, then the shorter of the two that start at 1 |
| `-3 -1 -2` | `-1 2 2` | all negative: the answer is the largest single element, not 0 |

## Constraints

- `1 <= n <= 200000`
- `-10^9 <= a[i] <= 10^9`

Use `input()` without a prompt message.
