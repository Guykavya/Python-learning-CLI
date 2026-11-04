# Two sum

Given `n` integers and a `target`, find **two different positions** `i < j` such that `a[i] + a[j] = target`. It is
guaranteed that **exactly one** such pair of positions exists. Print `i j` (0-based).

Trying every pair is `n^2 / 2` steps. Instead, for each value `x`, ask a dictionary: "have I already seen
`target - x`?"

## Input

- Line 1: `n target`.
- Line 2: `n` integers.

## Output

`i j` with `i < j`.

## Example

Input:

```
4 9
2 7 11 15
```

Output:

```
0 1
```

`2 + 7 = 9`. Values may repeat: for `3 3` with target `6` the answer is `0 1`.

## Constraints

- `2 <= n <= 200000`
- `-10^9 <= a[i], target <= 10^9`
- Exactly one valid pair of positions exists.
