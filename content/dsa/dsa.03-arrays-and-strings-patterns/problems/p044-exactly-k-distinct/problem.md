# Count subarrays with exactly k distinct values

Count the subarrays (contiguous, non-empty, counted by position) of `a` that contain **exactly** `k` different values.

A sliding window cannot do "exactly k" directly: when the window has exactly `k` distinct values, you cannot tell
whether to grow it or shrink it, because some shorter and some longer windows also qualify. But "**at most** k"
is easy with a window (it is the counting part of the previous fix-the-bugs problem), and

```
exactly(k) = atMost(k) - atMost(k - 1)
```

because a subarray with at most `k` distinct values has either exactly `k`, or at most `k - 1`.

## Input

- Line 1: `n` and `k`.
- Line 2: `n` integers.

## Output

One line: the number of subarrays with exactly `k` distinct values.

## Example

Input:

```
5 2
1 2 1 2 3
```

Output:

```
7
```

The seven subarrays: `[1,2]`, `[2,1]`, `[1,2]`, `[2,3]`, `[1,2,1]`, `[2,1,2]`, `[1,2,1,2]`.

## Constraints

- `1 <= n <= 200000`
- `1 <= k <= n`
- `1 <= a[i] <= 10^9`
- The answer can be larger than `2^31`; Python integers handle that.

Use `input()` without a prompt message.
