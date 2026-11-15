# Longest run of ones with k flips

The array holds only `0` and `1`. You may flip **at most** `k` zeros into ones. What is the longest run of
neighbouring ones you can get?

Put differently: find the longest subarray that contains at most `k` zeros.

## Input

- Line 1: `n` and `k`.
- Line 2: `n` values, each `0` or `1`.

## Output

One line: the longest possible run of ones.

## Example

Input:

```
11 2
1 1 1 0 0 0 1 1 1 1 0
```

Output:

```
6
```

Flip the zeros at positions 5 and 6 (1-based): `1 1 1 0 1 1 1 1 1 1 0` has the run `1 1 1 1 1 1` of length 6.

## Constraints

- `1 <= n <= 200000`
- `0 <= k <= n`

Use `input()` without a prompt message.
