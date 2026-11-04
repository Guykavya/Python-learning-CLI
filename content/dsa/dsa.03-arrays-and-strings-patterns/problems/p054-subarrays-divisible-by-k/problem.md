# Count subarrays with sum divisible by k

Count the subarrays (contiguous, non-empty, counted by position) whose sum is divisible by `k`.

This joins two earlier ideas. From prefix sums: the subarray `a[j..i-1]` has sum `P[i] - P[j]`. From modular
arithmetic: `P[i] - P[j]` is divisible by `k` exactly when `P[i] % k == P[j] % k`. So you only need to count **pairs
of prefixes with the same remainder**.

The values can be negative. In Python `-7 % 5` is `3` (the remainder always has the sign of `k`), which is exactly the
right "same remainder" test. Other languages give `-2` there, which is why solutions copied from them contain
`(x % k + k) % k`. Do **not** use `abs()`: `-1` and `1` have different remainders modulo 3.

## Input

- Line 1: `n` and `k`.
- Line 2: `n` integers.

## Output

One line: the number of subarrays whose sum is divisible by `k`.

## Example

Input:

```
6 5
4 5 0 -2 -3 1
```

Output:

```
7
```

Prefix sums: `0 4 9 9 7 4 5`. Their remainders modulo 5: `0 4 4 4 2 4 0`. The remainder 4 appears 4 times
(`4 * 3 / 2 = 6` pairs), the remainder 0 appears twice (1 pair), and 2 once (no pair): `6 + 1 = 7`. For example,
the pair `P[1] = 4`, `P[5] = 4` is the subarray `5 0 -2 -3` with sum 0.

## Constraints

- `1 <= n <= 200000`
- `1 <= k <= 10^9`
- `-10^9 <= a[i] <= 10^9`

Use `input()` without a prompt message.
