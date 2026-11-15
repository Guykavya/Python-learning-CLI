# Longest balanced subarray

An array contains only `0` and `1`. A subarray is **balanced** if it has as many `0`s as `1`s. Print the length of the
longest balanced subarray, or `0` if there is none.

Trick: replace every `0` by `-1`. Then a subarray is balanced exactly when its sum is `0`, that is when two prefix sums are
equal. Keep, for each prefix sum, the **first** index where it appeared. The longest block ends at the current index and
starts after that first index.

## Input

- Line 1: `n`.
- Line 2: `n` values, each `0` or `1`.

## Output

One integer.

## Example

Input:

```
7
0 1 0 1 1 1 0
```

Output:

```
4
```

The block `0 1 0 1` (positions 0 to 3) has two of each, and no longer block is balanced (the whole array has
4 ones and 3 zeros). The answer is `4`.

## Constraints

- `1 <= n <= 200000`
