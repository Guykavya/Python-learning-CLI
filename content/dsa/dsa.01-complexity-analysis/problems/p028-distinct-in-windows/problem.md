# Different values in every window

A sensor reports a reading code every minute. For every block of `k` consecutive minutes, report how many
**different** codes appeared in it.

`starter.py` builds `set(a[i:i + k])` for each block. That is correct, but it is O(n * k): with `n = 100000` and
`k = 50000` it takes minutes. Make it O(n).

## Input

- Line 1: `n` and `k`.
- Line 2: `n` integers.

## Output

One line with `n - k + 1` integers separated by single spaces: the count for the block starting at minute 1, then
minute 2, and so on.

## Example

Input:

```
7 3
1 2 1 3 4 2 3
```

Output:

```
2 3 3 3 3
```

Blocks: `1 2 1` (2 different), `2 1 3` (3), `1 3 4` (3), `3 4 2` (3), `4 2 3` (3).

## Constraints

- `1 <= k <= n <= 100000`
- codes are between `1` and `10^9`

Use `input()` without a prompt message.

## Before you code

When the block moves one step right, one reading leaves and one enters. Everything else stays. What do you need to
remember so that you can update the count instead of recounting? Careful: when a reading leaves, its code may still
be present elsewhere in the block.
