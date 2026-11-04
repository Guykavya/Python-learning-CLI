# Count the zero-sum subarrays

Count the contiguous subarrays `a[l..r]` whose elements add up to **0**. Remember the prefix-sum trick from dsa.03:
`sum(a[l..r]) = p[r+1] - p[l]`. The sum is 0 exactly when two prefix sums are **equal**. So count, for every prefix
sum, how many times it has been seen before.

## Input

- Line 1: `n`.
- Line 2: `n` integers.

## Output

One integer.

## Example

Input:

```
6
1 -1 2 -2 3 -3
```

Output:

```
6
```

Prefix sums `0 1 0 2 0 3 0`: the value `0` appears 4 times, giving `4 * 3 / 2 = 6` equal pairs. The values 1, 2, 3 appear
once each and give none. Zero-sum subarrays: `[1,-1]`, `[2,-2]`, `[3,-3]`, `[1,-1,2,-2]`, `[2,-2,3,-3]`, and the whole array.

## Constraints

- `1 <= n <= 200000`
- `-10^9 <= a[i] <= 10^9`
