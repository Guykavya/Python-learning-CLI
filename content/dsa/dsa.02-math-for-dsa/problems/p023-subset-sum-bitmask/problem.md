# Count subsets with a given sum

Given `n` integers and a target `t`, count the subsets (chosen by position) whose sum equals `t`. The empty subset has
sum 0. Two equal values at different positions give different subsets.

With `n <= 18` there are at most `2^18 = 262144` subsets, so you can look at all of them. Each subset is a number
`mask` from 0 to `2^n - 1`: bit `i` of `mask` says whether `a[i]` is in the subset.

## Input

- Line 1: `n` and `t`.
- Line 2: `n` integers.

## Output

One line: the number of subsets with sum `t`.

## Examples

| Input | Output | Why |
|---|---|---|
| `3 5` / `1 4 5` | `2` | `{1, 4}` and `{5}` |
| `3 0` / `1 -1 2` | `2` | the empty set and `{1, -1}` |
| `3 0` / `0 0 0` | `8` | every subset of three zeros has sum 0 |

## Constraints

- `1 <= n <= 18`
- `-1000 <= a[i] <= 1000`, `|t| <= 10^6`

Use `input()` without a prompt message. Adding up every subset from scratch costs `n` per subset. Can you get the sum of
`mask` from the sum of a smaller mask in O(1)? Remember `mask & (mask - 1)` removes the lowest set bit.
