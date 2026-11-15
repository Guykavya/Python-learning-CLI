# Count subarrays with sum k

A **subarray** is a run of neighbouring elements `a[i], a[i+1], ..., a[j]` (at least one element). Count how
many subarrays have a sum of exactly `k`.

The numbers may be **negative**, so a sliding window does not work here: adding an element can make the sum
smaller. Use prefix sums and a dictionary instead.

## Input

- Line 1: `n` and `k`.
- Line 2: `n` integers.

## Output

One line: the number of subarrays whose sum is `k`.

## Example

Input:

```
5 3
1 2 1 -1 3
```

Output:

```
5
```

The five subarrays are `1 2`, `2 1`, `1 2 1 -1`, `1 -1 3` and `3`. Two subarrays with the same values at
different positions count twice.

## Constraints

- `1 <= n <= 200000`
- `-10^4 <= a[i] <= 10^4`
- `-10^9 <= k <= 10^9`

An O(n^2) loop over all start and end positions is too slow for `n = 200000`; aim for one pass.
Use `input()` without a prompt message.
