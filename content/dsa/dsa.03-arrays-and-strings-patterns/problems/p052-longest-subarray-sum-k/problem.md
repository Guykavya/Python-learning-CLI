# Longest subarray with sum k

Find the length of the **longest** contiguous subarray whose sum is exactly `k`. Print `0` if there is none.

The values can be **negative**, so a sliding window does not work: adding an element can make the sum go down,
and shrinking can make it go up, so you never know which end to move. Use prefix sums instead.

With `P[i]` = the sum of the first `i` elements (`P[0] = 0`), the subarray `a[j..i-1]` has sum `P[i] - P[j]`. For a
fixed end `i`, you want the **earliest** `j` with `P[j] = P[i] - k`. A dictionary that remembers the **first**
index where each prefix value appeared answers that in O(1).

## Input

- Line 1: `n` and `k`.
- Line 2: `n` integers.

## Output

One line: the length of the longest subarray with sum `k`, or `0`.

## Example

Input:

```
7 3
1 -1 5 -2 3 -4 2
```

Output:

```
6
```

Four subarrays have sum 3: `1 -1 5 -2` (positions 1 to 4), `5 -2` (3 to 4), `3` (5 to 5) and
`-1 5 -2 3 -4 2` (2 to 7). The longest has length 6.

Prefix sums: `P = 0 1 0 5 3 6 2 4`. At the end, `P[7] = 4`, and `4 - 3 = 1` first appeared as `P[1]`, so the subarray
is positions 2 to 7. The prefix value 0 appears twice (`P[0]` and `P[2]`); for the longest subarray, the first one is
the one to keep.

## Constraints

- `1 <= n <= 200000`
- `-10^4 <= a[i] <= 10^4`
- `-10^9 <= k <= 10^9`

Use `input()` without a prompt message.
