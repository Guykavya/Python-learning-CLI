# Count the pairs with a given sum

Count the pairs of **positions** `i < j` with `a[i] + a[j] = k`. Equal values at different positions are different
pairs, so `3 3 3` with `k = 6` has **3** pairs. For each element `x` the number of earlier elements that complete it
is the count of `k - x` seen so far.

## Input

- Line 1: `n k`.
- Line 2: `n` integers.

## Output

One integer: the number of pairs.

## Example

Input:

```
5 6
1 5 3 3 3
```

Output:

```
4
```

`(1, 5)` and three pairs among the three `3`s: `1 + 5` once and `3 + 3` three times = 4.

## Constraints

- `1 <= n <= 200000`
- `-10^9 <= a[i], k <= 10^9`
- The answer can be as large as about `2 * 10^10`. Python integers do not overflow.
